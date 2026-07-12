FROM python:3.11-slim

# Cài đặt các thư viện hệ thống bắt buộc cho OpenCV và Tkinter GUI chạy trên Linux
RUN apt-get update && apt-get install -y \
    python3-tk \
    libgl1-mesa-glx \
    libglib2.2-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Thay vì đọc file requirements.txt, ta cài đặt trực tiếp luôn để tránh lỗi file trống/lỗi phân quyền trên CI
RUN pip install --no-cache-dir opencv-python pillow numpy

# Copy toàn bộ source code vào container
COPY . .

CMD ["python", "app.py"]