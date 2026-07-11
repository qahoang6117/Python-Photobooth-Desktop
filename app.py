import os
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2

class PhotoboothApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Python Photobooth")
        self.window.geometry("900x650")
        
        # Khởi tạo thư mục lưu ảnh
        self.output_dir = "photobooth_photos"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Kết nối Camera (0 là camera mặc định của laptop)
        self.cap = cv2.VideoCapture(0)
        
        # Biến trạng thái
        self.countdown_value = 0
        self.flash_active = False

        self.setup_ui()
        self.update_frame() # Bắt đầu vòng lặp hiển thị camera

    def setup_ui(self):
        # Khung chứa Camera (Bên trái)
        self.left_frame = ttk.Frame(self.window)
        self.left_frame.pack(side=tk.LEFT, padx=20, pady=20)

        self.camera_label = ttk.Label(self.left_frame)
        self.camera_label.pack()

        # Khung điều khiển và xem lại (Bên phải)
        self.right_frame = ttk.Frame(self.window)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)

        # Nút Chụp Ảnh
        self.capture_btn = ttk.Button(self.right_frame, text="CHỤP ẢNH (Space)", command=self.start_countdown)
        self.capture_btn.pack(pady=20, ipadx=10, ipady=10)
        self.window.bind('<space>', lambda event: self.start_countdown())

        # Khung hiển thị ảnh vừa chụp
        self.preview_title = ttk.Label(self.right_frame, text="Ảnh vừa chụp:", font=("Arial", 12, "bold"))
        self.preview_title.pack(pady=10)
        
        self.preview_label = ttk.Label(self.right_frame, text="Chưa có ảnh nào")
        self.preview_label.pack(pady=10)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Lật ảnh theo chiều ngang để giống gương
            frame = cv2.flip(frame, 1)
            self.current_frame = frame.copy()

            # Hiệu ứng nháy Flash trắng khi chụp
            if self.flash_active:
                frame[:] = 255
                self.flash_active = False

            # Vẽ số đếm ngược lên màn hình camera
            if self.countdown_value > 0:
                cv2.putText(frame, str(self.countdown_value), (260, 280), 
                            cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 255), 10, cv2.LINE_AA)

            # Chuyển đổi định dạng ảnh sang Tkinter
            cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2_image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
            
        self.window.after(15, self.update_frame)

    def start_countdown(self):
        self.capture_btn.config(state=tk.DISABLED)
        self.run_countdown(3) # Đếm ngược từ 3 giây

    def run_countdown(self, value):
        self.countdown_value = value
        if value > 0:
            self.window.after(1000, lambda: self.run_countdown(value - 1))
        else:
            self.flash_active = True
            self.take_photo()
            self.capture_btn.config(state=tk.NORMAL)

    def take_photo(self):
        if hasattr(self, 'current_frame'):
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f"photo_{timestamp}.jpg")
            
            # Lưu ảnh
            cv2.imwrite(filename, self.current_frame)

            # Hiển thị ảnh vừa chụp lên khung xem lại (Preview)
            preview_img = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(preview_img)
            img.thumbnail((250, 250))
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.preview_label.imgtk = imgtk
            self.preview_label.configure(image=imgtk)

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoboothApp(root)
    root.mainloop()