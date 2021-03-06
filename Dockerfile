FROM python:3.8-slim
COPY . /app
WORKDIR /app
EXPOSE 5000
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["ground.py"]
