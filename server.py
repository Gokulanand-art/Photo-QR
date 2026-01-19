from flask import Flask, send_file, render_template, abort
import os
import time
import threading
import uuid

app = Flask(__name__)

IMAGE_DIR = "images"
SESSIONS = {}
DELETE_AFTER = 45

os.makedirs(IMAGE_DIR, exist_ok=True)

def auto_delete(token):
    time.sleep(DELETE_AFTER)
    if token in SESSIONS:
        path = SESSIONS[token]["path"]
        if os.path.exists(path):
            os.remove(path)
        del SESSIONS[token]

@app.route("/create", methods=["POST"])
def create():
    token = uuid.uuid4().hex
    path = f"{IMAGE_DIR}/{token}.jpg"

    with open(path, "wb") as f:
        f.write(b"")

    SESSIONS[token] = {
        "path": path,
        "used": False
    }

    threading.Thread(target=auto_delete, args=(token,), daemon=True).start()
    return {"token": token}

@app.route("/scan/<token>")
def scan(token):
    if token not in SESSIONS or SESSIONS[token]["used"]:
        return "Session expired", 410
    return render_template("download.html", token=token)

@app.route("/image/<token>")
def image(token):
    if token not in SESSIONS:
        abort(404)
    return send_file(SESSIONS[token]["path"])

@app.route("/download/<token>")
def download(token):
    if token not in SESSIONS or SESSIONS[token]["used"]:
        abort(410)

    SESSIONS[token]["used"] = True
    path = SESSIONS[token]["path"]

    def cleanup():
        time.sleep(1)
        if os.path.exists(path):
            os.remove(path)
        del SESSIONS[token]

    threading.Thread(target=cleanup, daemon=True).start()
    return send_file(path, as_attachment=True)

@app.route("/upload/<token>", methods=["POST"])
def upload(token):
    if token not in SESSIONS:
        abort(404)

    with open(SESSIONS[token]["path"], "wb") as f:
        f.write(request.data)

    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)