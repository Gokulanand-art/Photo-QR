from flask import Flask, send_file, render_template, abort
import os, time, uuid, threading

app = Flask(__name__, template_folder="templates")

IMAGE_PATH = "captured.jpg"

# token -> timestamp
SESSIONS = {}

DELETE_AFTER = 45  # seconds


def auto_delete(token):
    time.sleep(DELETE_AFTER)
    if token in SESSIONS:
        if os.path.exists(IMAGE_PATH):
            os.remove(IMAGE_PATH)
        del SESSIONS[token]
        print("Auto deleted image & token")


@app.route("/create")
def create_session():
    token = uuid.uuid4().hex
    SESSIONS[token] = time.time()

    t = threading.Thread(target=auto_delete, args=(token,))
    t.start()

    return {"url": f"/session/{token}"}


@app.route("/session/<token>")
def view_image(token):
    if token not in SESSIONS:
        return "Session expired / Invalid QR", 410

    if not os.path.exists(IMAGE_PATH):
        return "No image available", 404

    return render_template("download.html", token=token)


@app.route("/download/<token>")
def download(token):
    if token not in SESSIONS:
        abort(410)

    if not os.path.exists(IMAGE_PATH):
        abort(404)

    del SESSIONS[token]

    return send_file(
        IMAGE_PATH,
        as_attachment=True,
        download_name="photo.jpg"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)