#!/usr/bin/env python3
import sys
import math
from datetime import datetime, timezone, timedelta


# --------------------------------------------------------------------
#  gfdcfd interpolation matrix (standalone, no imports!)
# --------------------------------------------------------------------
def gfdcfd(X, XARR):
    """
    Build finite-difference coefficient matrix for interpolating at point X
    from grid XARR using Fornberg's method.
    """
    import numpy as np

    XARR = np.array(XARR, float)
    NNDS = len(XARR)

    h = XARR - X
    COEFM = np.zeros((NNDS, NNDS), float)

    for nder in range(NNDS):
        for inode in range(NNDS):
            if nder == 0:
                COEFM[inode, nder] = 1.0
            else:
                COEFM[inode, nder] = COEFM[inode, nder-1] * (h[inode] / nder)

    return np.linalg.inv(COEFM)


# --------------------------------------------------------------------
#  1-D interpolation using gfdcfd
# --------------------------------------------------------------------
def interp_1d(x, xarr, yarr, n=6):
    import numpy as np

    # exact match?
    where = np.where(np.isclose(xarr, x))[0]
    if len(where) > 0:
        return float(yarr[where[0]])

    if x < xarr[0] or x > xarr[-1]:
        return None

    idx = np.searchsorted(xarr, x)
    half = n // 2
    i0 = max(0, idx - half)
    i1 = i0 + n
    if i1 > len(xarr):
        i1 = len(xarr)
        i0 = i1 - n

    xa = xarr[i0:i1]
    ya = yarr[i0:i1]

    M = gfdcfd(x, xa)
    w = M[0, :]          # row 0 -> interpolation weights
    return float((w * ya).sum())


# --------------------------------------------------------------------
#  Read AK135 P-wave table (STRICT 900-values-per-depth)
# --------------------------------------------------------------------
def read_tt_table(filename):
    import numpy as np

    with open(filename, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    i = 0
    n = len(lines)

    # ---- depth samples ----
    while i < n:
        if "Number of depth samples" in lines[ i ]:
            ndepth = int(lines[i].split()[0])
            i += 1
            depths = []
            while len(depths) < ndepth:
                depths.extend(map(float, lines[i].split()))
                i += 1
            break
        i += 1

    # ---- distance samples ----
    while i < n:
        if "Number of distance samples" in lines[i]:
            ndist = int(lines[i].split()[0])
            i += 1
            distances = []
            while len(distances) < ndist:
                distances.extend(map(float, lines[i].split()))
                i += 1
            break
        i += 1

    # ---- read each depth block ----
    tt_blocks = []

    while i < n:
        if lines[i].startswith("# Travel time at depth"):
            i += 1
            block = []
            for _ in range(ndist):
                block.append(float(lines[i]))
                i += 1
            tt_blocks.append(block)
        else:
            i += 1

    return ( 
        np.array(depths, float),
        np.array(distances, float),
        np.array(tt_blocks, float)
    )


# --------------------------------------------------------------------
#  2-D interpolation (distance then depth)
# --------------------------------------------------------------------
def interp_tt(depth, dist, depths, distances, tt):
    import numpy as np

    if depth < depths[0] or depth > depths[-1]:
        return None
    if dist < distances[0] or dist > distances[-1]:
        return None

    # interpolate horizontally for each depth
    col = np.array([
        interp_1d(dist, distances, tt_row)
        for tt_row in tt
    ])

    # interpolate vertically in depth
    return interp_1d(depth, depths, col)


# --------------------------------------------------------------------
#  Haversine → distance in degrees
# --------------------------------------------------------------------
def haversine_deg(lat1, lon1, lat2, lon2):
    rlat1 = math.radians(lat1)
    rlat2 = math.radians(lat2)
    rlon1 = math.radians(lon1)
    rlon2 = math.radians(lon2)

    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1

    a = math.sin(dlat/2)**2 + math.cos(rlat1)*math.cos(rlat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return math.degrees(c)


# --------------------------------------------------------------------
#  Parse origin time in UTC
# --------------------------------------------------------------------
def parse_origin_time(s):
    # epoch seconds?
    try:
        sec = float(s)
        return datetime(1970,1,1,tzinfo=timezone.utc) + timedelta(seconds=sec)
    except:
        pass

    # ISO8601, assume UTC if no timezone
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt


# --------------------------------------------------------------------
#  main
# --------------------------------------------------------------------
def main():
    if len(sys.argv) < 7:
        print("Usage:")
        print("  python arrival_time_standalone.py station_lat station_lon "
              "event_lat event_lon event_dep_km ak135_P1.txt "
              "[--origin_time YYYY-mm-ddTHH:MM:SS.sss]")
        sys.exit(1)

    station_lat = float(sys.argv[1])
    station_lon = float(sys.argv[2])
    event_lat   = float(sys.argv[3])
    event_lon   = float(sys.argv[4])
    event_dep   = float(sys.argv[5])
    ttfile      = sys.argv[6]

    # optional origin time
    origin_time = None
    if len(sys.argv) >= 9 and sys.argv[7] == "--origin_time":
        origin_time = parse_origin_time(sys.argv[8])

    # load table
    depths, distances, tt = read_tt_table(ttfile)

    # compute distance
    dist_deg = haversine_deg(station_lat, station_lon, event_lat, event_lon)

    # travel time
    tt_sec = interp_tt(event_dep, dist_deg, depths, distances, tt)

    print(f"Distance_deg = {dist_deg:.4f}")
    print(f"Travel_time_s = {tt_sec:.4f}")

    if origin_time:
        arrival = origin_time + timedelta(seconds=tt_sec)
        print("Arrival_time_UTC =", arrival.isoformat(timespec="milliseconds"))


if __name__ == "__main__":
    main()
