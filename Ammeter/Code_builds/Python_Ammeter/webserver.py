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
    <body style="margin:0; background:black; text-align:center;">

    <img id="stream" src="/frame.jpg" width="800">

    <br><br>

    <button onclick="sendCmd('UP')">Scale Up</button>
    <button onclick="sendCmd('DOWN')">Scale Down</button>

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