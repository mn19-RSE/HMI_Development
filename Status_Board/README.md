# General Status Board

## NOTE:
This will heavily use and reference the [Database_Development](https://github.com/mn19-RSE/Database_Development) repo.

## Purpose:
Remote device that will display relavent data by reading from the database files that the SlowTasks are writing to. 

## Initial Plan:
Use one ESP32 board as a bridge between the custom database to MCU API and the MCU displaying info. This is needed only for remote displays that are not on the controls LAN. The top method for ESP32 peer-to-peer wireless communication over this distance is the ESPNOW protocol. This may or may not use the [Controls Dashboard](/Controls_Dashboard/README.md) as the ESPNOW bridge. 

## Updated Plan:
### Local Development
- Develop for a Raspberry Pi instead of MCU 
- Develop a python API locally (controls network) that will query a database file for most recent value in a desired channel
    - API will make the most recent data available for a Pi
    - API will only store the most recent value in the channel
- A Raspberry Pi will make request to the API for the data and then display it graphically using the Tkinter library
### Future Steps
- Implementation will involve using a network DMZ to handle communication between UW WIFI and controls network

## Relavent Data Ideas:
- Radiation levels
- Main cooling water loop temps
- Simplified vacuum status
