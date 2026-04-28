from flask import Flask, send_file
import socket

app = Flask(__name__)

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

@app.route("/")
def index():
    return """
    <html>
    <head>
    <style>
    html, body {
        margin: 0;
        height: 100%;
        background: black;
        overflow: hidden;
        font-family: Arial, sans-serif;
    }

    /* MAIN LAYOUT */
    #app {
        display: flex;
        height: 100vh;
        width: 100vw;
    }

    /* IMAGE AREA */
    #viewer {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        background: black;
    }

    #stream {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }

    /* CONTROL PANEL */
    #controls {
        width: 220px;
        background: #111;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 15px;
        padding: 20px;
        box-sizing: border-box;
    }

    /* BUTTON STYLE */
    button {
        padding: 12px;
        border: none;
        border-radius: 10px;
        background: #2d6cdf;
        color: white;
        font-size: 14px;
        cursor: pointer;
        transition: 0.2s;
    }

    button:hover {
        background: #1f4fa3;
        transform: scale(1.05);
    }

    button:active {
        transform: scale(0.95);
    }
    </style>
    </head>

    <body>

    <div id="app">

        <!-- IMAGE SIDE -->
        <div id="viewer">
            <img id="stream" src="/frame.jpg">
        </div>

        <!-- CONTROLS SIDE -->
        <div id="controls">
            <button onclick="sendCmd('UP')">Scale Up</button>
            <button onclick="sendCmd('DOWN')">Scale Down</button>
        </div>

    </div>

    <script>
    function updateImage() {
        const img = document.getElementById("stream");
        img.src = "/frame.jpg?t=" + new Date().getTime();
    }
    setInterval(updateImage, 100);

    function sendCmd(cmd) {
        fetch("/cmd/" + cmd);
    }
    </script>

    </body>
    </html>
    """

@app.route('/frame.jpg')
def frame():
    return send_file("/tmp/frame.jpg", mimetype='image/jpeg')

@app.route('/cmd/<command>')
def cmd(command):
    sock.sendto(command.encode(), (UDP_IP, UDP_PORT))
    return "OK"

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)