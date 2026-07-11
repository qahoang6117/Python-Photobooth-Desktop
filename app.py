import os
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np

class PhotoboothApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Python Photobooth v2.0 - Filters")
        self.window.geometry("950x700")
        
        self.output_dir = "photobooth_photos"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.cap = cv2.VideoCapture(0)
        
        self.countdown_value = 0
        self.flash_active = False
        
        # Biến quản lý bộ lọc và độ sáng
        self.current_filter = "Mặc định"
        self.brightness_value = 0 # Từ -100 đến 100

        self.setup_ui()
        self.update_frame()

    def setup_ui(self):
        # Khung chứa Camera (Bên trái)
        self.left_frame = ttk.Frame(self.window)
        self.left_frame.pack(side=tk.LEFT, padx=20, pady=20)

        self.camera_label = ttk.Label(self.left_frame)
        self.camera_label.pack()

        # Khung điều khiển và chức năng (Bên phải)
        self.right_frame = ttk.Frame(self.window)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Nút Chụp Ảnh
        self.capture_btn = ttk.Button(self.right_frame, text="📸 CHỤP ẢNH (Space)", command=self.start_countdown)
        self.capture_btn.pack(pady=10, fill=tk.X, ipady=5)
        self.window.bind('<space>', lambda event: self.start_countdown())

        # Khung hiển thị ảnh vừa chụp (Preview thu nhỏ)
        self.preview_title = ttk.Label(self.right_frame, text="Ảnh vừa chụp:", font=("Arial", 11, "bold"))
        self.preview_title.pack(pady=5)
        self.preview_label = ttk.Label(self.right_frame, text="Chưa có ảnh nào")
        self.preview_label.pack(pady=5)

        # ----- KHUNG CHỌN BỘ LỌC MÀU -----
        filter_frame = ttk.LabelFrame(self.right_frame, text=" BỘ LỌC VÀ CHỈNH SỬA ")
        filter_frame.pack(pady=15, fill=tk.X, padx=5, ipady=10)

        ttk.Label(filter_frame, text="Chọn Filter:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=5)
        
        # Các nút chọn bộ lọc nhanh
        btn_grid = ttk.Frame(filter_frame)
        btn_grid.pack(fill=tk.X, padx=10)

        filters = ["Mặc định", "Trắng đen", "Cổ điển", "Lạnh"]
        for f in filters:
            btn = ttk.Button(btn_grid, text=f, command=lambda name=f: self.change_filter(name))
            btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        # Thanh kéo chỉnh độ sáng (Slider)
        ttk.Label(filter_frame, text="Độ sáng:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=10)
        self.bright_slider = ttk.Scale(filter_frame, from_=-60, to=60, orient=tk.HORIZONTAL, command=self.change_brightness)
        self.bright_slider.set(0) # Mặc định ở giữa
        self.bright_slider.pack(fill=tk.X, padx=10)

    def change_filter(self, name):
        self.current_filter = name

    def change_brightness(self, val):
        self.brightness_value = int(float(val))

    def apply_effects(self, frame):
        # 1. Xử lý độ sáng (Brightness)
        if self.brightness_value != 0:
            # Dùng np.clip để tránh hiện tượng tràn pixel (>255 hoặc <0)
            frame = np.int16(frame)
            frame = frame + self.brightness_value
            frame = np.clip(frame, 0, 255)
            frame = np.uint8(frame)

        # 2. Xử lý Bộ lọc màu (Filters)
        if self.current_filter == "Trắng đen":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR) # Đưa về lại 3 kênh màu để đồng bộ hiển thị
        
        elif self.current_filter == "Cổ điển": # Màu ngả vàng/ấm (Sepia)
            kernel = np.array([[0.272, 0.534, 0.131],
                               [0.349, 0.686, 0.168],
                               [0.393, 0.769, 0.189]])
            frame = cv2.transform(frame, kernel)
            frame = np.clip(frame, 0, 255).astype(np.uint8)
            
        elif self.current_filter == "Lạnh": # Tăng sắc xanh dương (Cool tone)
            # Tăng kênh màu B (Blue) và giảm kênh R (Red)
            B, G, R = cv2.split(frame)
            B = cv2.add(B, 30)
            R = cv2.subtract(R, 10)
            frame = cv2.merge((B, G, R))

        return frame

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            
            # Áp dụng bộ lọc màu và độ sáng đã chọn lên frame hình
            frame = self.apply_effects(frame)
            
            # Lưu lại bản có hiệu ứng để tí chụp ảnh lưu xuống máy
            self.current_frame = frame.copy()

            if self.flash_active:
                frame[:] = 255
                self.flash_active = False

            if self.countdown_value > 0:
                cv2.putText(frame, str(self.countdown_value), (260, 280), 
                            cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 255), 10, cv2.LINE_AA)

            # Vẽ chữ hiển thị tên Filter đang dùng ở góc camera cho chuyên nghiệp
            cv2.putText(frame, f"Filter: {self.current_filter}", (15, 35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

            cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2_image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
            
        self.window.after(15, self.update_frame)

    def start_countdown(self):
        self.capture_btn.config(state=tk.DISABLED)
        self.run_countdown(3)

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
            
            # Lưu ảnh gốc đã qua bộ lọc màu thành công
            cv2.imwrite(filename, self.current_frame)

            # Hiển thị ảnh vừa chụp ra preview
            preview_img = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(preview_img)
            img.thumbnail((180, 180))
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