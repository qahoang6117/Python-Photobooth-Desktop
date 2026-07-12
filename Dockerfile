FROM python:3.11-slim

# Cài đặt các thư viện hệ thống cần thiết cho OpenCV và Tkinter GUI
RUN apt-get update && apt-get install -y \
    python3-tk \
    libgl1-mesa-glx \
    libglib2.2-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Lệnh chạy ứng dụng
CMD ["python", "app.py"]