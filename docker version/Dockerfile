FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p db

# Buộc Python dùng UTF-8
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
ENV PYTHONUTF8=1

# Expose dải port cho các node (5000-5002)
EXPOSE 5000 5001 5002

CMD ["python", "main.py"]
