FROM python:3.12-slim

# Cài đặt FFmpeg và các công cụ cần thiết cho âm thanh
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ source code
COPY . .

# Tạo thư mục dữ liệu và logs
RUN mkdir -p data logs temp

CMD ["python", "main.py"]
