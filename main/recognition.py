import cv2
from main import config

# Tạo dictionary tĩnh cho danh sách ID và tên người dùng
face_names = {
    1: "Nguyen Van A",
    2: "Tran Thi B",
    3: "Le Van C",
    11:"Phuc"
    # Thêm các ID và tên khác tùy thuộc vào dữ liệu bạn có
}

# Khởi tạo bộ nhận diện
recognizer = config.recognizer
recognizer.read('../trainer/trainer.yml')

face_detector = config.face_detector
font = cv2.FONT_HERSHEY_PLAIN

# Cấu hình camera
cam = cv2.VideoCapture(0)
cam.set(3, 640)  # Chiều rộng
cam.set(4, 480)  # Chiều cao

minW = 0.1 * cam.get(3)
minH = 0.1 * cam.get(4)

while True:
    ret, img = cam.read()
    img = cv2.flip(img, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Phát hiện khuôn mặt
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(int(minW), int(minH)))

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

        if confidence < 100:
            # Lấy tên từ dictionary tĩnh face_names
            name = face_names.get(id, "Unknown")
            confidence_text = "  {0}%".format(round(100 - confidence))
        else:
            name = "unknown"
            confidence_text = "  {0}%".format(round(100 - confidence))

        cv2.putText(img, str(name), (x + 5, y - 5), font, 1, (0, 255, 0), 2)
        cv2.putText(img, confidence_text, (x + 5, y + h + 20), font, 1, (0, 255, 0), 1)

    cv2.imshow('Detect', img)

    # Nhấn 'ESC' hoặc 'q' để thoát
    k = cv2.waitKey(10) & 0xff
    if k == 27 or k == ord('q'):
        break

# Đóng kết nối và giải phóng tài nguyên
cam.release()
cv2.destroyAllWindows()
