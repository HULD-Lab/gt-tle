FROM python:3.8
WORKDIR /app
EXPOSE 5000
EXPOSE 9191
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /app
CMD ["uwsgi","--http","0.0.0.0:5000","--wsgi-file","ground.py","--callable","app","--processes","1","--threads","2","--stats","0.0.0.0:9191"]
