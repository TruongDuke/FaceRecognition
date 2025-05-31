import os
import tkinter as tk
import util
import subprocess
from PIL import Image, ImageTk
import cv2
import datetime

class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")

        self.login_button_main_window = util.get_button(self.main_window, 'Login', 'lightgreen', self.login)
        self.login_button_main_window.place(x=750, y=300)

        self.register_button_main_window = util.get_button(self.main_window, 'Sign Up', 'gray', self.register_new_user, fg='black')
        self.register_button_main_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)
        self.log_path = './log.txt'

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
        unkown_img_path = './.tmp.jpg'
        cv2.imwrite(unkown_img_path, self.most_recent_capture_arr)
        output= str(subprocess.check_output(['face_recognition', self.db_dir, unkown_img_path]))
        name=output.split(',')[1][:-3].strip()
        print(name)
        if name in['unknown_person','no_persons_found']:
            util.msg_box('Please register new user or Try agian')
            
        else:
            util.msg_box('Welcome','Welcome {}'.format(name))    
            with open(self.log_path,'a') as f:
                f.write('{},{}\n'.format(name,datetime.datetime.now()))
                f.close()
        os.remove(unkown_img_path)    

    def register_new_user(self):
     # Create a new window for user registration
     self.register_new_user_window = tk.Toplevel(self.main_window)
     self.register_new_user_window.geometry("1200x520+370+120")
 
     # Add widgets to the new window
     self.text_label_register_new_user = tk.Label(self.register_new_user_window, text="Please input your username:")
     self.text_label_register_new_user.place(x=750, y=70)

     # Using util.get_entry_text function for input field
     self.entry_text = util.get_entry_text(self.register_new_user_window)
     self.entry_text.place(x=750, y=150)

     # Button to accept registration
     self.accept_button = tk.Button(self.register_new_user_window, text="Accept", command=self.accept_register_new_user)
     self.accept_button.place(x=750, y=300)

     # Button to try again
     self.try_again_button = tk.Button(self.register_new_user_window, text="Try Again", command=self.try_again_register_new_user)
     self.try_again_button.place(x=750, y=400)

     # Create and place capture label for webcam feed in the register window
     self.capture_label = util.get_img_label(self.register_new_user_window)
     self.capture_label.place(x=10, y=0, width=700, height=500)

     # Ensure webcam feed is continuously updated in the registration window
     self.add_img_to_label(self.capture_label)

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        # Store a copy of the current frame for further processing
        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def accept_register_new_user(self):
        # Get the username and show a registration success message
        username = self.entry_text.get(1.0, "end-1c")
        print(f"User '{username}' has been registered successfully!")
        image_path = os.path.join(self.db_dir, '{}.jpg'.format(username))
        cv2.imwrite(image_path, self.register_new_user_capture)
        util.msg_box('Success','User was registered successfully!')
        self.register_new_user_window.destroy()

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def start(self):
        self.main_window.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()