# Raspberry Pi5 Powered Networked Ammeter
Built around Keithley 18000-20 current amplifier

## Python scripts:
### total_system.py
- Uses pygame to display graphics on screen
- Handles button pressses and netwroked communications
- Takes screenshot every 10 seconds for webserver
### websever.py
- Hosts HTML page
- Displays most recent screenshot
- Displays a "scale up" and a "scale down" button

## System startup
### During testing
1. SSH into vsg@ammeter.local  (192.168.42.50)
2. git pull HMI_Development 
3. Start total_system.py and webserver.py

### Final Implementation
1. Create Systemd sevice file with path to python files
    1. $ sudo nano /etc/systemd/system/ammeter.service 
    2. Paste in following: <br> 
        [Unit]
        Description=Ammeter system code  # Brief description of the service
        After=network.target  # Start AFTER the network is ready (optional: adjust based on dependencies)
        
        [Service]
        User=your_username  # Run as your user (or "root" for system-level tasks)
        WorkingDirectory=/home/vdg  # Directory to run the program from (optional)
        ExecStart=/usr/bin/python3 /home/vdg/HMI_Development/Code_builds/Python_Ammeter/  # path to total_system
        Type=simple  # "simple" for foreground processes; "oneshot" for scripts that run once
        Restart=on-failure  # Restart if the program crashes (optional: "always", "never", etc.)
        
        [Install]
        WantedBy=multi-user.target  # Start when the system reaches multi-user mode (boot)
    3. sudo systemctl daemon-reload
    4. sudo systemctl start ammeter.service
2. SSH vsg@ammeter.local to pull updates and observe system health
3. View logs to troubleshoot issues
    - journalctl -u ammeter.service  # View all logs

