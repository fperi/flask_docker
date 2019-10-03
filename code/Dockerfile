# import from image on dockerhub
FROM alpine

# copy requirements to container
COPY requirements.txt /tmp/requirements.txt

# run the following commands to install required libraries
RUN apk add --no-cache \
    curl \
    python3 \
    bash \
    nginx \
    uwsgi \
    uwsgi-python3 \
    supervisor && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    pip3 install -r /tmp/requirements.txt && \
    rm /etc/nginx/conf.d/default.conf && \
    rm -r /root/.cache

# copy configuration files for nginx, uwsgi and supervisor
COPY nginx.conf /etc/nginx/
COPY flask-site-nginx.conf /etc/nginx/conf.d/
COPY uwsgi.ini /etc/uwsgi/
COPY supervisord.conf /etc/

# copy main code
COPY /app /project/app
COPY /yabasic /project/yabasic
WORKDIR /project

# execute supervisor to start the container
CMD ["/usr/bin/supervisord"]
