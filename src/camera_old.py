from flask import Flask, Response, render_template, jsonify, request as flask_req
import cv2
import post_ip

app = Flask(__name__)
port = 5001
ngrok_ip = post_ip.get_and_post_ip()


def generate_frames(cameraIndex=0):
    camera = cv2.VideoCapture(cameraIndex)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ip")
def ip():
    return jsonify(
        {
            "ip": ngrok_ip,
        }
    )


@app.route("/video1")
def video_feed():
    camera_index = 0
    return Response(
        generate_frames(camera_index),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )
    
@app.route("/video2")
def video_feed2():
    camera_index = 2
    return Response(
        generate_frames(camera_index),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )

if __name__ == "__main__":
    # app.run(ssl_context=('cert.pem', 'key.pem'),debug=True, host='0.0.0.0', port=5001)
    # app.run(debug=True, host="0.0.0.0", port=port)
    app.run(debug=True, port=port)
