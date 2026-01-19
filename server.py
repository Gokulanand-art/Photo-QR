from flask import Flask, send_file, render_template
import os
import threading
import time

app = Flask(__name__)

# ===== GLOBAL STATE =====
ACTIVE_IMAGE = None
ACTIVE = False
LOCK = threading.Lock()

IMAGE_PATH = "captured.jpg"
AUTO_DELETE_SECONDS = 45


# ===== AUTO DELETE THREAD =====
def auto_delete():
    global ACTIVE, ACTIVE_IMAGE
    time.sleep(AUTO_DELETE_SECONDS)

    with LOCK:
        if ACTIVE and ACTIVE_IMAGE and os.path.exists(ACTIVE_IMAGE):
            os.remove(ACTIVE_IMAGE)
            print("⏱ Auto-deleted image")

        ACTIVE = False
        ACTIVE_IMAGE = None


# ===== QR ENTRY POINT (STATIC QR) =====
@app.route("/")
@app.route("/scan")
def scan():
    with LOCK:
        if not ACTIVE or not ACTIVE_IMAGE:
            return "No image available"

    return render_template("download.html")


# ===== DOWNLOAD IMAGE =====
@app.route("/download")
def download():
    global ACTIVE, ACTIVE_IMAGE

    with LOCK:
        if not ACTIVE or not ACTIVE_IMAGE:
            return "Session expired"

        try:
            response = send_file(ACTIVE_IMAGE, as_attachment=True)
            os.remove(ACTIVE_IMAGE)
            print("⬇ Image downloaded and deleted")
        except Exception as e:
            return f"Error: {e}"

        ACTIVE = False
        ACTIVE_IMAGE = None

    return response


# ===== FUNCTION CALLED BY main.py =====
def activate_image():
    global ACTIVE, ACTIVE_IMAGE

    with LOCK:
        ACTIVE_IMAGE = IMAGE_PATH
        ACTIVE = True

    threading.Thread(target=auto_delete, daemon=True).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)