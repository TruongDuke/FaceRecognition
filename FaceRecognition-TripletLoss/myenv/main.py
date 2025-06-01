import os
import cv2
import torch
import numpy as np
import tkinter as tk
import datetime
from PIL import Image, ImageTk
from facenet_pytorch import MTCNN, InceptionResnetV1
import threading
import util

# ====== Load models ======
mtcnn = MTCNN(keep_all=False)
facenet = InceptionResnetV1(pretrained='vggface2').eval()

# ====== Helper function ======
def get_face_encoding(image):
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face = mtcnn(Image.fromarray(img_rgb))
    if face is None:
        return None, None
    with torch.no_grad():
        embedding = facenet(face.unsqueeze(0))
    return embedding[0].numpy(), None

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ====== App Class ======
class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")

        self.login_button_main_window = util.get_button(self.main_window, 'Login', 'lightgreen', self.login_thread)
        self.login_button_main_window.place(x=750, y=300)

        self.register_button_main_window = util.get_button(self.main_window, 'Sign Up', 'gray', self.register_new_user, fg='black')
        self.register_button_main_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.db_dir = './db'
        os.makedirs(self.db_dir, exist_ok=True)
        self.log_path = './log.txt'
        self.known_faces = self.load_known_faces()

        self.cap = cv2.VideoCapture(0)
        self.process_webcam()

    def load_known_faces(self):
        known_faces = {}
        for file in os.listdir(self.db_dir):
            if file.endswith(('.jpg', '.png')):
                img = cv2.imread(os.path.join(self.db_dir, file))
                enc, _ = get_face_encoding(img)
                if enc is not None:
                    name = os.path.splitext(file)[0]
                    known_faces[name] = enc
        return known_faces

    def process_webcam(self):
        ret, frame = self.cap.read()
        if not ret:
            self.webcam_label.after(50, self.process_webcam)
            return

        self.most_recent_capture_arr = frame.copy()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self.webcam_label.imgtk = imgtk
        self.webcam_label.configure(image=imgtk)

        self.webcam_label.after(30, self.process_webcam)

    def login_thread(self):
        threading.Thread(target=self.login, daemon=True).start()

    def login(self):
        rgb = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        unknown_enc, _ = get_face_encoding(rgb)
        if unknown_enc is None:
            util.msg_box("Error", "Không phát hiện khuôn mặt!")
            return

        for name, known_enc in self.known_faces.items():
            sim = cosine_similarity(known_enc, unknown_enc)
            if sim > 0.8:
                util.msg_box('Welcome', f'Welcome {name}')
                with open(self.log_path, 'a') as f:
                    f.write(f'{name},{datetime.datetime.now()}')
                return

        util.msg_box('Unknown', 'Không nhận diện được. Vui lòng đăng ký.')

    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")

        tk.Label(self.register_new_user_window, text="Please input your username:").place(x=750, y=70)
        self.entry_text = util.get_entry_text(self.register_new_user_window)
        self.entry_text.place(x=750, y=150)

        tk.Button(self.register_new_user_window, text="Accept", command=self.accept_register_new_user).place(x=750, y=300)
        tk.Button(self.register_new_user_window, text="Try Again", command=self.try_again_register_new_user).place(x=750, y=400)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)
        self.add_img_to_label(self.capture_label)

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)
        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def accept_register_new_user(self):
        username = self.entry_text.get(1.0, "end-1c").strip()
        if not username:
            util.msg_box('Error', 'Tên người dùng không được để trống!')
            return

        save_path = os.path.join(self.db_dir, f'{username}.jpg')
        cv2.imwrite(save_path, self.register_new_user_capture)

        rgb = cv2.cvtColor(self.register_new_user_capture, cv2.COLOR_BGR2RGB)
        enc, _ = get_face_encoding(rgb)
        if enc is not None:
            self.known_faces[username] = enc
            util.msg_box('Success', 'Đăng ký thành công!')
        else:
            util.msg_box('Error', 'Không tìm thấy khuôn mặt trong ảnh đã lưu!')
        self.register_new_user_window.destroy()

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def start(self):
        self.main_window.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()
