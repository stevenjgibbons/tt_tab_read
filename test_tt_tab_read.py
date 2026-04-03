#!/usr/bin/env python3
import sys
import numpy as np

def gfdcfd(X, XARR):
    XARR = np.array(XARR, dtype=float)
    NNDS = len(XARR)
    
    # Check uniqueness

    if len(np.unique(XARR)) != NNDS:
        raise ValueError("Grid points in XARR are not distinct.")

    # Compute h_i = x_i - X
    h = XARR - X
    
    # Build matrix
    COEFM = np.zeros((NNDS, NNDS), dtype=float)
    for nder in range(NNDS):
        for inode in range(NNDS):
            if nder == 0:
                COEFM[inode, nder] = 1.0
            else:
                COEFM[inode, nder] = COEFM[inode, nder - 1] * (h[inode] / nder)
    
    # Invert
    return np.linalg.inv(COEFM)

def read_tt_table(filename):
    depths = []
    distances = []
    tt_blocks = []

    with open(filename, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    i = 0
    n = len(lines)

    # depths
    while i < n:
        if "Number of depth samples" in lines[i]:
            ndepth = int(lines[i].split()[0])
            i += 1
            while len(depths) < ndepth:
                depths.extend(map(float, lines[i].split()))
                i += 1
            break
        i += 1

    # distances
    while i < n:
        if "Number of distance samples" in lines[i]:
            ndist = int(lines[i].split()[0])
            i += 1
            while len(distances) < ndist:
                distances.extend(map(float, lines[i].split()))
                i += 1
            break
        i += 1

    # travel times
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

    return np.array(depths), np.array(distances), np.array(tt_blocks)


# ------------------------------------------------------------
# CORRECT gfdcfd interpolation
# ------------------------------------------------------------
def interp_1d(x, xarr, yarr, n=6):

    # exact grid hit → return exact value
    if x in xarr:
        return yarr[np.where(xarr == x)[0][0]]

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
    w = M[0, :]          # ✅ CORRECT: ROW 0
    return float(np.dot(w, ya))


def interp_tt(depth, dist, depths, distances, tt):

    if depth < depths[0] or depth > depths[-1]:
        return None
    if dist < distances[0] or dist > distances[-1]:
        return None

    # horizontal interpolation
    vals = np.array([
        interp_1d(dist, distances, row)
        for row in tt
    ])

    # vertical interpolation
    return interp_1d(depth, depths, vals)

def main():
    if len(sys.argv) != 4:
        print("Usage: python test_tt_tab_read.py dist_in_deg depth_in_km ttfilename")
        return

    dist = float(sys.argv[1])
    depth = float(sys.argv[2])
    fname = sys.argv[3]

    depths, distances, tt = read_tt_table(fname)
    val = interp_tt(depth, dist, depths, distances, tt)

    if val is None:
        print("-1.0")
    else:
        print(f"{val:.4f}")

if __name__ == "__main__":
    main()
