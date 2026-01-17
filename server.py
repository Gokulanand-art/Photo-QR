from flask import Flask, send_file, render_template
import os, threading, shutil, time

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE = os.path.join(BASE_DIR, "captured.jpg")
TEMP_IMAGE = os.path.join(BASE_DIR, "temp_download.jpg")

timer = None

def auto_delete():
    if os.path.exists(IMAGE):
        os.remove(IMAGE)
        print("Image auto-deleted after 45 seconds")

def start_timer():
    global timer
    if timer:
        timer.cancel()
    timer = threading.Timer(45, auto_delete)
    timer.start()

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
    if not os.path.exists(IMAGE):
        return "No image"

    # Copy to temp file (prevents Windows lock issue)
    shutil.copy(IMAGE, TEMP_IMAGE)

    # Delete original AFTER copy
    os.remove(IMAGE)
    print("Original image deleted")

    response = send_file(TEMP_IMAGE, as_attachment=True)

    # Delete temp file AFTER sending
    threading.Thread(target=cleanup_temp).start()

    return response

def cleanup_temp():
    time.sleep(2)
    if os.path.exists(TEMP_IMAGE):
        os.remove(TEMP_IMAGE)
        print("Temp image deleted")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)