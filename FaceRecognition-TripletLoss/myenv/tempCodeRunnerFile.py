import tkinter as tk

class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")
    
    # Phương thức start() phải nằm trong lớp App
    def start(self):
        self.main_window.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()