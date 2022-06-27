FROM python:3.9-slim
RUN apt-get update
RUN apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . ./
CMD gunicorn -b 0.0.0.0:80 app:server
