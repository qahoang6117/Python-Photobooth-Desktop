FROM python:3.11-slim

# Cài đặt các thư viện hệ thống bắt buộc cho OpenCV và Tkinter
RUN apt-get update && apt-get install -y \
    python3-tk \
    libgl1-mesa-glx \
    libglib2.2-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài đặt trực tiếp thư viện
RUN pip install --no-cache-dir opencv-python pillow numpy

# Copy code vào container
COPY . .

CMD ["python", "app.py"]