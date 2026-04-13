from flask import Flask, send_file

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <html>
    <body style="margin:0; background:black;">
        <img src="/frame.jpg" id="img" width="100%">
        <script>
            setInterval(() => {
                document.getElementById("img").src = "/frame.jpg?" + new Date().getTime();
            }, 100); // ~10 FPS
        </script>
    </body>
    </html>
    """

@app.route("/frame.jpg")
def frame():
    return send_file("/tmp/frame.jpg", mimetype="image/jpeg")

app.run(host="0.0.0.0", port=5000)