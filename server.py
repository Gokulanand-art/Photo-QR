from flask import Flask, request, send_file, render_template
import os
import threading
import time

app = Flask(__name__)

IMAGE_PATH = "captured.jpg"
DELETE_AFTER = 45  # seconds
timer_thread = None


# -------------------------
# Background auto-delete
# -------------------------
def auto_delete_image():
    global IMAGE_PATH
    time.sleep(DELETE_AFTER)
    if os.path.exists(IMAGE_PATH):
        os.remove(IMAGE_PATH)
        print("🗑️ Image auto-deleted after 45 seconds")


# -------------------------
# Upload image from laptop
# -------------------------
@app.route("/upload", methods=["POST"])
def upload():
    global timer_thread

    file = request.files["image"]
    file.save(IMAGE_PATH)
    print("📸 Image received from laptop")

    # Start delete timer in background
    timer_thread = threading.Thread(target=auto_delete_image)
    timer_thread.daemon = True
    timer_thread.start()

    return "Image uploaded", 200


# -------------------------
# Show image page (QR)
# -------------------------
@app.route("/")
def index():
    if not os.path.exists(IMAGE_PATH):
        return "No image available"
    return render_template("download.html")


# -------------------------
# Download + delete image
# -------------------------
@app.route("/download")
def download():
    if not os.path.exists(IMAGE_PATH):
        return "Image not found"

    response = send_file(IMAGE_PATH, as_attachment=True)

    # Delete AFTER sending
    def delete_after_send():
        time.sleep(1)
        if os.path.exists(IMAGE_PATH):
            os.remove(IMAGE_PATH)
            print("🗑️ Image deleted after download")

    threading.Thread(target=delete_after_send).start()
    return response


# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)