import tkinter as tk
import util
from PIL import Image, ImageTk
import cv2

class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")

        self.login_button_main_window = util.get_button(self.main_window, 'Login', 'lightgreen', self.login)
        self.login_button_main_window.place(x=750, y=300)

        self.register_button_main_window = util.get_button(self.main_window, 'Sign Up', 'gray', self.register, fg='black')
        self.register_button_main_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def login(self):
        pass

    def register(self):
        # Tạo cửa sổ con cho đăng ký người dùng mới
        self.register_user_window = tk.Toplevel(self.main_window)
        self.register_user_window.geometry("1200x520+370+120")

        # Thêm các widget vào cửa sổ con
        self.text_label = tk.Label(self.register_user_window, text="Please input your username:")
        self.text_label.place(x=750, y=70)

        self.entry_text = tk.Entry(self.register_user_window, font=("Arial", 32))
        self.entry_text.place(x=750, y=150)

        self.accept_button = tk.Button(self.register_user_window, text="Accept", command=self.accept_register_new_user)
        self.accept_button.place(x=750, y=300)

        self.try_again_button = tk.Button(self.register_user_window, text="Try Again", command=self.try_again_register_new_user)
        self.try_again_button.place(x=750, y=400)

    def accept_register_new_user(self):
        # Lấy tên người dùng và hiển thị thông báo đăng ký thành công
        username = self.entry_text.get()
        print(f"User '{username}' has been registered successfully!")

    def try_again_register_new_user(self):
        self.register_user_window.destroy()

    def start(self):
        self.main_window.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()