A little tool to extract traveltime estimates from a "Bayesloc" style traveltime table.  

[![SQAaaS badge](https://github.com/EOSC-synergy/SQAaaS/raw/master/badges/badges_150x116/badge_software_bronze.png)](https://api.eu.badgr.io/public/assertions/FLJEa_XhRnaNU_Cnht6rvA "SQAaaS bronze badge achieved")  

[![SQAaaS badge shields.io](https://img.shields.io/badge/sqaaas%20software-bronze-e6ae77)](https://api.eu.badgr.io/public/assertions/FLJEa_XhRnaNU_Cnht6rvA "SQAaaS bronze badge achieved")  

https://sqaaas.eosc-synergy.eu/full-assessment/report/https://raw.githubusercontent.com/eosc-synergy/tt_tab_read.assess.sqaaas/main/.report/assessment_output.json  

```
Usage:
  python arrival_time_standalone.py station_lat station_lon event_lat \
       event_lon event_dep_km ak135_P1.txt [--origin_time YYYY-mm-ddTHH:MM:SS.sss]
```

e.g.

```
python arrival_time.py 60.0  0.0 80.05 10.0  0.0  ak135_P1.dat \
    --origin_time 2026-04-02T12:34:56.789
python arrival_time.py  0.0  0.0 10.00  0.0 22.0  ak135_S1.dat \
    --origin_time 2026-04-02T12:34:56.789
```

This results in the following output:  
```
Distance_deg = 20.2682
Travel_time_s = 277.0176
Arrival_time_UTC = 2026-04-02T12:39:33.806+00:00
Distance_deg = 10.0000
Travel_time_s = 253.7600
Arrival_time_UTC = 2026-04-02T12:39:10.549+00:00
```
