from flask import Flask, send_file, render_template, request
import os, threading, time, shutil

app = Flask(__name__)

IMAGE = "captured.jpg"
TEMP_IMAGE = "temp_download.jpg"

delete_timer = None
image_seen = False

def auto_delete():
    global image_seen
    if os.path.exists(IMAGE):
        os.remove(IMAGE)
    image_seen = False

def start_timer():
    global delete_timer
    if delete_timer:
        delete_timer.cancel()
    delete_timer = threading.Timer(45, auto_delete)
    delete_timer.start()

def image_watcher():
    global image_seen
    while True:
        if os.path.exists(IMAGE) and not image_seen:
            image_seen = True
            start_timer()
        time.sleep(1)

threading.Thread(target=image_watcher, daemon=True).start()

@app.route("/")
def home():
    if os.path.exists(IMAGE):
        return render_template("download.html")
    return "<h3>No image available</h3>"

@app.route("/preview")
def preview():
    if os.path.exists(IMAGE):
        return send_file(IMAGE)
    return "No image"

@app.route("/download")
def download():
    global delete_timer, image_seen

    if not os.path.exists(IMAGE):
        return "No image"

    shutil.copy(IMAGE, TEMP_IMAGE)
    os.remove(IMAGE)
    image_seen = False

    if delete_timer:
        delete_timer.cancel()

    response = send_file(TEMP_IMAGE, as_attachment=True)
    threading.Thread(target=cleanup_temp).start()
    return response

def cleanup_temp():
    time.sleep(2)
    if os.path.exists(TEMP_IMAGE):
        os.remove(TEMP_IMAGE)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["image"]
    file.save(IMAGE)
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)