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
        self.window.title("MÁY CHỤP ẢNH TỰ ĐỘNG - PHOTOBOOTH Studio")
        self.window.geometry("1000x700")
        self.window.configure(bg="#f0f2f5") # Đổi màu nền sang xám nhẹ hiện đại
        
        # Cấu hình style chung cho giao diện hiện đại hơn
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', font=('Helvetica', 10), background='#f0f2f5')
        self.style.configure('TButton', font=('Helvetica', 10, 'bold'), padding=6)
        self.style.configure('Action.TButton', font=('Helvetica', 12, 'bold'), background='#007bff', foreground='white')
        
        self.output_dir = "photobooth_photos"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.cap = cv2.VideoCapture(0)
        
        self.countdown_value = 0
        self.flash_active = False
        self.current_filter = "Mặc định"
        self.brightness_value = 0

        self.setup_ui()
        self.update_frame()

    def setup_ui(self):
        # 1. TIÊU ĐỀ ỨNG DỤNG (TOP)
        title_label = tk.Label(self.window, text="✨ KỶ NIỆM PHOTOBOOTH ✨", font=("Helvetica", 18, "bold"), bg="#f0f2f5", fg="#333333")
        title_label.pack(pady=10)

        # KHUNG CHÍNH CHỨA 2 BÊN (LEFT & RIGHT)
        main_container = ttk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # 2. KHUNG CHỨA CAMERA (BÊN TRÁI)
        left_frame = ttk.Frame(main_container, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tạo viền đen bao quanh Camera cho chuyên nghiệp
        camera_border = tk.Frame(left_frame, bg="#333333", padx=3, pady=3)
        camera_border.pack()

        self.camera_label = ttk.Label(camera_border)
        self.camera_label.pack()

        # 3. KHUNG CHỨA BẢNG ĐIỀU KHIỂN (BÊN PHẢI)
        right_frame = ttk.Frame(main_container, padding=10, width=320)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False) # Giữ nguyên độ rộng khung phải

        # ---- KHU VỰC CHỤP ẢNH ----
        self.capture_btn = ttk.Button(right_frame, text="📸 CHỤP ẢNH (Phím Space)", style='Action.TButton', command=self.start_countdown)
        self.capture_btn.pack(fill=tk.X, ipady=10, pady=(0, 15))
        self.window.bind('<space>', lambda event: self.start_countdown())

        # ---- KHU VỰC BỘ LỌC MÀU ----
        filter_group = ttk.LabelFrame(right_frame, text=" 🎨 BỘ LỌC HÌNH ẢNH ", padding=10)
        filter_group.pack(fill=tk.X, pady=(0, 15))

        # Grid chia các nút bộ lọc thành 2 hàng - 2 cột trực quan
        grid_frame = ttk.Frame(filter_group)
        grid_frame.pack(fill=tk.X, pady=5)

        filters_config = [
            ("🔄 Mặc định", "Mặc định", 0, 0),
            ("🌓 Trắng đen", "Trắng đen", 0, 1),
            ("🍂 Cổ điển", "Cổ điển", 1, 0),
            ("❄️ Lạnh", "Lạnh", 1, 1)
        ]

        for text, name, r, c in filters_config:
            btn = ttk.Button(grid_frame, text=text, command=lambda n=name: self.change_filter(n))
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            grid_frame.grid_columnconfigure(c, weight=1)

        # ---- KHU VỰC ĐỘ SÁNG ----
        brightness_group = ttk.LabelFrame(right_frame, text=" ☀️ ĐỘ SÁNG MÀN HÌNH ", padding=10)
        brightness_group.pack(fill=tk.X, pady=(0, 15))

        self.bright_slider = ttk.Scale(brightness_group, from_=-60, to=60, orient=tk.HORIZONTAL, command=self.change_brightness)
        self.bright_slider.set(0)
        self.bright_slider.pack(fill=tk.X, pady=5)

        # ---- KHU VỰC XEM LẠI ẢNH VỪA CHỤP ----
        preview_group = ttk.LabelFrame(right_frame, text=" 🖼️ ẢNH VỪA CHỤP MỚI NHẤT ", padding=10)
        preview_group.pack(fill=tk.BOTH, expand=True)

        self.preview_label = tk.Label(preview_group, text="Chưa chụp tấm nào", fg="#888888", bg="#ffffff", relief=tk.SOLID, bd=1)
        self.preview_label.pack(fill=tk.BOTH, expand=True, pady=5)

    def change_filter(self, name):
        self.current_filter = name

    def change_brightness(self, val):
        self.brightness_value = int(float(val))

    def apply_effects(self, frame):
        if self.brightness_value != 0:
            frame = np.int16(frame) + self.brightness_value
            frame = np.clip(frame, 0, 255).astype(np.uint8)

        if self.current_filter == "Trắng đen":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        elif self.current_filter == "Cổ điển":
            kernel = np.array([[0.272, 0.534, 0.131],
                               [0.349, 0.686, 0.168],
                               [0.393, 0.769, 0.189]])
            frame = cv2.transform(frame, kernel)
            frame = np.clip(frame, 0, 255).astype(np.uint8)
        elif self.current_filter == "Lạnh":
            B, G, R = cv2.split(frame)
            B = cv2.add(B, 30)
            R = cv2.subtract(R, 10)
            frame = cv2.merge((B, G, R))
        return frame

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = self.apply_effects(frame)
            self.current_frame = frame.copy()

            if self.flash_active:
                frame[:] = 255
                self.flash_active = False

            if self.countdown_value > 0:
                cv2.putText(frame, str(self.countdown_value), (260, 280), 
                            cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 255), 10, cv2.LINE_AA)

            # Chỉ báo filter đang bật hiển thị tinh tế ở góc trên bên trái
            cv2.rectangle(frame, (5, 5), (170, 35), (50, 50, 50), -1)
            cv2.putText(frame, f"Cam: {self.current_filter}", (12, 26), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

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
            cv2.imwrite(filename, self.current_frame)

            # Render ảnh thu nhỏ vào khung Preview trắng thanh lịch ở góc phải
            preview_img = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(preview_img)
            
            # Tính toán kích thước fit vừa vặn khung hiển thị bên phải mà không méo ảnh
            img.thumbnail((260, 220))
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.preview_label.imgtk = imgtk
            self.preview_label.configure(image=imgtk, text="") # Xóa chữ mặc định đi khi có ảnh

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoboothApp(root)
    root.mainloop()