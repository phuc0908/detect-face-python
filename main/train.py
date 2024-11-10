import numpy as np
from PIL import Image
import os
from main import config

recognizer = config.recognizer

def getImages(dataset_path):
    faceSamples = []
    ids = []

    # Duyệt qua từng thư mục người dùng trong dataset
    for user_folder in os.listdir(dataset_path):
        user_path = os.path.join(dataset_path, user_folder)

        # Kiểm tra nếu là thư mục
        if os.path.isdir(user_path):
            try:
                # Lấy ID người dùng từ tên thư mục
                user_id = int(user_folder)

                # Lấy tất cả các ảnh trong thư mục của user
                imgpaths = [os.path.join(user_path, f) for f in os.listdir(user_path) if os.path.isfile(os.path.join(user_path, f))]

                for imgpath in imgpaths:
                    # Chuyển ảnh sang grayscale
                    PIL_img = Image.open(imgpath).convert('L')
                    img_numpy = np.array(PIL_img, 'uint8')

                    # Phát hiện khuôn mặt
                    faces = config.face_detector.detectMultiScale(img_numpy)
                    if len(faces) == 0:
                        print(f"Bỏ qua file {imgpath} vì không tìm thấy khuôn mặt.")
                        continue

                    for (x, y, w, h) in faces:
                        faceSamples.append(img_numpy[y:y+h, x:x+w])
                        ids.append(user_id)
            except (ValueError, IndexError) as e:
                print(f"Bỏ qua thư mục {user_folder} do lỗi: {e}")

    return faceSamples, ids

print("Đang huấn luyện...")
faces, ids = getImages("../dataset")

# Kiểm tra dữ liệu không rỗng
if faces and ids:
    recognizer.train(faces, np.array(ids))
    recognizer.write('../trainer/trainer.yml')
    print("Huấn luyện hoàn tất và lưu vào file 'trainer/trainer.yml'.")
else:
    print("Lỗi: Dữ liệu khuôn mặt hoặc ID bị rỗng.")
