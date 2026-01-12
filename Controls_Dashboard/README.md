# Controls_Dahsboard

## NOTE:
This will heavily use and reference the [Database_Development](https://github.com/mn19-RSE/Database_Development) repo.

## Purpose:
This will most likely be the first MCU that will read from the SLowTask database file and display information on a set custom GUI mounted on the VDG control panel. This will be live data that is beter represented by gauges, dials, bar graphs, etc instead of X-Y time-series plots like SlowDash can handle just fine. 

## Initial Plan:
Use an ESP32-P4 Nano in conjunction with the custom API to read information from the database files over the network via the onboard LAN port. 