from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import dlib
import imutils
import time
import numpy as np
from scipy.spatial import distance as dist
from imutils import face_utils

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable SocketIO with CORS support

# Global variables for the drowsiness detection
alarm_status = False
alarm_status2 = False
saying = False
COUNTER = 0

# Load the required models
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 30
YAWN_THRESH = 20

# Function to calculate eye aspect ratio (EAR)
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Function to calculate EAR and lip distance
def final_ear(shape):
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)
    ear = (leftEAR + rightEAR) / 2.0
    return (ear, leftEye, rightEye)

# Function to calculate lip distance for yawning
def lip_distance(shape):
    top_lip = shape[50:53]
    top_lip = np.concatenate((top_lip, shape[61:64]))
    low_lip = shape[56:59]
    low_lip = np.concatenate((low_lip, shape[65:68]))
    top_mean = np.mean(top_lip, axis=0)
    low_mean = np.mean(low_lip, axis=0)
    distance = abs(top_mean[1] - low_mean[1])
    return distance

# Function to stream video frames over socket
def generate_video_stream():
    global alarm_status, alarm_status2, COUNTER

    vs = cv2.VideoCapture(0)  # Use the default camera
    time.sleep(1.0)

    while True:
        success, frame = vs.read()
        if not success:
            break

        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in rects:
            rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            # Drowsiness detection
            ear, leftEye, rightEye = final_ear(shape)
            distance = lip_distance(shape)

            if ear < EYE_AR_THRESH:
                COUNTER += 1
                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    if not alarm_status:
                        alarm_status = True
                    cv2.putText(frame, "DROWSINESS ALERT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                COUNTER = 0
                alarm_status = False

            if distance > YAWN_THRESH:
                cv2.putText(frame, "Yawn Alert", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Draw contours around eyes and mouth
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
            lip = shape[48:60]
            cv2.drawContours(frame, [lip], -1, (0, 255, 0), 1)

        # Encode frame as JPEG and send via WebSocket
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        socketio.emit('video_frame', {'frame': frame})

@app.route('/')
def index():
    return render_template('index.html')  # Render the index.html file

@socketio.on('connect')
def connect():
    print('Client connected')

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

# Start the video stream in the background
def background_video_stream():
    while True:
        generate_video_stream()

if __name__ == '__main__':
    socketio.start_background_task(background_video_stream)  # Start the video stream as a background task
    socketio.run(app, port=5001, debug=True)
