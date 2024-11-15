import cv2
import mysql.connector
from main import config
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime

# Kết nối với MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="detect_face_app"
)

# Tạo con trỏ và truy vấn danh sách ID và tên từ MySQL
cursor = db.cursor()
cursor.execute("SELECT id, name FROM users")

# Tạo dictionary face_names từ kết quả truy vấn
face_names = {user_id: name for user_id, name in cursor.fetchall()}

# Đóng con trỏ và kết nối
cursor.close()

# Khởi tạo bộ nhận diện
recognizer = config.recognizer
recognizer.read('../trainer/trainer.yml')

face_detector = config.face_detector

# Cấu hình camera
cam = cv2.VideoCapture(0)
cam.set(3, 640)  # Chiều rộng
cam.set(4, 480)  # Chiều cao

minW = 0.1 * cam.get(3)
minH = 0.1 * cam.get(4)

# Chọn font Unicode
font_path = "path/to/arial.ttf"  # Đường dẫn tới file font Unicode, ví dụ "arial.ttf"
font_pil = ImageFont.truetype(font_path, 20)

# Lưu ngày nhận diện của mỗi người (theo user_id)
recognized_today = {}

while True:
    ret, img = cam.read()
    img = cv2.flip(img, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Phát hiện khuôn mặt
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(int(minW), int(minH)))

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 1)
        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

        if confidence < 100:
            # Lấy tên từ dictionary face_names
            name = face_names.get(id, "Unknown")
            confidence_text = "  {0}%".format(round(100 - confidence))

            if name != "Unknown":
                # Kiểm tra xem người này đã được nhận diện trong ngày hôm nay chưa
                today_date = datetime.now().strftime('%Y-%m-%d')

                # Truy vấn để kiểm tra xem người dùng đã có chấm công hôm nay chưa
                cursor = db.cursor()
                query = """
                    SELECT COUNT(*) FROM schedule 
                    WHERE user_id = %s AND DATE(start_time) = %s
                """
                cursor.execute(query, (id, today_date))
                count = cursor.fetchone()[0]

                if count == 0:  # Chưa có chấm công trong ngày
                    try:
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        insert_query = """
                            INSERT INTO schedule (user_id, start_time)
                            VALUES (%s, %s)
                        """
                        cursor.execute(insert_query, (id, current_time))
                        db.commit()
                        cursor.close()
                    except mysql.connector.Error as e:
                        print(f"Lỗi khi cập nhật vào bảng schedule: {e}")
                else:
                    print(f"User {name} đã chấm công trong ngày hôm nay.")

        else:
            name = "unknown"
            confidence_text = "  {0}%".format(round(100 - confidence))

        # Chuyển hình ảnh thành định dạng PIL
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        # Vẽ tên và độ tự tin bằng Pillow
        draw.text((x + 5, y - 25), str(name), font=font_pil, fill=(255, 255, 0, 255))
        draw.text((x + 5, y + h + 5), confidence_text, font=font_pil, fill=(255, 255, 0, 255))

        # Chuyển lại thành định dạng OpenCV
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    cv2.imshow('Detect', img)

    # Nhấn 'ESC' hoặc 'q' để thoát
    k = cv2.waitKey(10) & 0xff
    if k == 27 or k == ord('q'):
        break

# Đóng kết nối và giải phóng tài nguyên
cam.release()
cv2.destroyAllWindows()
db.close()
