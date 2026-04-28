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
        Description=Ammeter system code
        After=network.target
        
        [Service]
        User=root
        WorkingDirectory=/home/vdg
        ExecStart=/usr/bin/python3 /home/vdg/HMI_Development/Ammeter/Code_builds/Python_Ammeter/main.py 
        Type=simple
        Restart=on-failure 
        
        [Install]
        WantedBy=multi-user.target
    3. sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable myservice
sudo systemctl start myservice
2. SSH vsg@ammeter.local to pull updates and observe system health
3. View logs to troubleshoot issues
    - journalctl -u ammeter.service

