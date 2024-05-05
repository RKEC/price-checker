FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV SENDER_EMAIL=""
ENV SENDER_PASSWORD=""
ENV TO_EMAIL=""
ENV URL=""
ENV PRICE=

CMD ["python", "main.py"]