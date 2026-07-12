FROM python:3.11-slim

# Cập nhật các gói thư viện hệ thống mới nhất tương thích với OpenCV và Tkinter
RUN apt-get update && apt-get install -y \
    python3-tk \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài đặt các thư viện Python cần thiết
RUN pip install --no-cache-dir opencv-python pillow numpy

COPY . .

CMD ["python", "app.py"]