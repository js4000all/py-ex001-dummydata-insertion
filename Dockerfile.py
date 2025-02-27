FROM python:alpine
RUN set -x \
    && apk add curl git gcc musl-dev linux-headers \
    && python3 -m pip install influxdb-client \
    && python3 -m pip install mysql-connector-python pymysql \
    && python3 -m pip install jupyterlab \
    && addgroup -S appgroup \
    && adduser -S appuser -G appgroup

WORKDIR /home/appuser
USER appuser
