FROM python:3.6.2

ENV APP_PATH /opt/luminate-client
ENV APP_CONFIGURATION_PATH ${APP_PATH}/conf
ENV APP_DEBUG_LOGS_PATH ${APP_PATH}/logs

RUN mkdir -p ${APP_PATH} ${APP_CONFIGURATION_PATH} ${APP_DEBUG_LOGS_PATH}
WORKDIR ${APP_PATH}

COPY luminate_python.py ${APP_PATH}/luminate_python.py
COPY luminate_client.py ${APP_PATH}/luminate_client.py

COPY requirements.txt ${APP_CONFIGURATION_PATH}/requirements.txt
RUN pip install --no-cache-dir -r ${APP_CONFIGURATION_PATH}/requirements.txt

ENTRYPOINT ["python", "./luminate_client.py"]