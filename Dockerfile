# Start with a Python image.
FROM python:3.7.2-alpine3.9

#######################################
# Set These Values
ARG appname=pythia
#ARG appwheelfile=mytest-1.0.0-py3-none-any.whl
# Set Port in CMD
#######################################

ENV FLASK_APP $appname
ENV FLASK_ENV development

# Install some necessary things.
# RUN apt-get update


# Copy all our files into the image.
#RUN mkdir /home
WORKDIR /home
#COPY $appwheelfile /home/$appwheelfile
COPY $appname /home/$appname
COPY requirements.txt /home/requirements.txt
COPY files /home/files
COPY ._serve_flask_dev.py /home/._serve_flask_dev.py
COPY ._serve_flask_prod.py /home/._serve_flask_prod.py
COPY ._serve_waitress.py /home/._serve_waitress.py
COPY ._serve_gunicorn.py /home/._serve_gunicorn.py

# Install our app
# RUN pip install flask
RUN pip install -r requirements.txt
# RUN flask init-db

#########################################################
# Specify the command to run when the image is run.
# CMD ["flask","run","--host","0.0.0.0", "--port", "5000"]
CMD ["python3","._serve_waitress.py"]
#########################################################
