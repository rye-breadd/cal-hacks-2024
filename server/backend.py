from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import dlib
import imutils
import time
import numpy as np
from scipy.spatial import distance as dist
from imutils import face_utils
from threading import Thread
import playsound

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

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

# Function to handle alarm sound
def sound_alarm(path):
    global alarm_status, alarm_status2, saying
    while alarm_status:
        playsound.playsound(path)
    if alarm_status2 and not saying:
        saying = True
        playsound.playsound(path)
        saying = False

# Video streaming generator with drowsiness detection
def generate_frames():
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
                        t = Thread(target=sound_alarm, args=('Alert.WAV',))
                        t.daemon = True
                        t.start()
                    cv2.putText(frame, "DROWSINESS ALERT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                COUNTER = 0
                alarm_status = False

            if distance > YAWN_THRESH:
                cv2.putText(frame, "Yawn Alert", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if not alarm_status2 and not saying:
                    alarm_status2 = True
                    t = Thread(target=sound_alarm, args=('Alert.WAV',))
                    t.daemon = True
                    t.start()
            else:
                alarm_status2 = False

            # Draw contours around eyes and mouth
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
            lip = shape[48:60]
            cv2.drawContours(frame, [lip], -1, (0, 255, 0), 1)

        # Encode frame and yield it
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed', methods=['GET'])
def video_feed():
    response =  Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.route('/api/debug', methods=['GET'])
def connect_response():
    return jsonify({"message": "Flask Server Works"})

if __name__ == '__main__':
    app.run(port=5001, debug=True)



