import sys
import cv2
import mysql.connector
import os
from main import config

# Lấy ID người dùng từ đối số dòng lệnh (user_id)
# if len(sys.argv) != 2:
#     print("Lỗi: Bạn phải cung cấp user_id.")
#     sys.exit(1)

user_id = 11 # sys.argv[1]

# Kết nối với MySQL
db = mysql.connector.connect(
    host=config.DB_HOST,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    database=config.DB_NAME
)

# Tạo con trỏ để thực hiện truy vấn
cursor = db.cursor()

# Tạo bảng nếu chưa có
cursor.execute("""
CREATE TABLE IF NOT EXISTS face_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    face_id VARCHAR(50),
    image_path VARCHAR(255)
)
""")

# Khởi động camera
cam = cv2.VideoCapture(0)
cam.set(3, 640)  # Đặt chiều rộng
cam.set(4, 480)  # Đặt chiều cao

print("Khởi động camera...")

# Tạo thư mục 'dataset' nếu chưa tồn tại
dataset_dir = os.path.abspath('../dataset')
if not os.path.exists(dataset_dir):
    os.makedirs(dataset_dir)

# Tạo thư mục riêng cho người dùng nếu chưa tồn tại
user_folder = os.path.join(dataset_dir, str(user_id))
if not os.path.exists(user_folder):
    os.makedirs(user_folder)

count = 0

while True:
    ret, img = cam.read()
    if not ret:
        print("Không thể truy cập vào camera")
        break

    img = cv2.flip(img, 1)  # Lật ảnh theo chiều dọc
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = config.face_detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        count += 1

        # Đường dẫn ảnh trong thư mục của người dùng
        image_path = os.path.join(user_folder, f'{user_id}_{count}.jpg')

        # Lưu ảnh vào thư mục của người dùng
        cv2.imwrite(image_path, gray[y:y+h, x:x+w])

        # Lưu đường dẫn ảnh vào MySQL
        cursor.execute("INSERT INTO face_data (face_id, image_path) VALUES (%s, %s)", (user_id, image_path))
        db.commit()

    # Hiển thị ảnh
    cv2.imshow('image', img)

    # Điều kiện thoát
    k = cv2.waitKey(100) & 0xff
    if k == 27 or count >= 20:
        print("Đã chụp đủ ảnh hoặc người dùng đã nhấn ESC")
        break

# Giải phóng camera và đóng cửa sổ
print("\nThoát")
cam.release()
cv2.destroyAllWindows()

# Đóng kết nối
cursor.close()
db.close()
