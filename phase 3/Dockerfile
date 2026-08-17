FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY start.sh .

RUN chmod +x start.sh

EXPOSE 8501
EXPOSE 8502

CMD ["./start.sh"]

