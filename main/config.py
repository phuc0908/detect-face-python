import cv2
import os

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "detect_face_app"

face_detector = cv2.CascadeClassifier(os.path.join(os.getcwd(), 'haarcascade.xml'))
recognizer = cv2.face.LBPHFaceRecognizer_create()
