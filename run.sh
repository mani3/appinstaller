#!/usr/bin/env sh

echo 'Start appinstall...'
ENV_DIR=flask
if [ ! -d "${ENV_DIR}" ]; then
  ./env.sh ${ENV_DIR}
fi

LOG_DIR=/var/log/appinstaller
ERROR_LOG=${LOG_DIR}/error_log
ACCESS_LOG=${LOG_DIR}/access_log
if [ ! -d "${LOG_DIR}" ]; then
  sudo mkdir -p "${LOG_DIR}"
  sudo chown $(logname) "${LOG_DIR}"
  touch "${ERROR_LOG}"
  touch "${ACCESS_LOG}"
fi

source ${ENV_DIR}/bin/activate

# Run migration
if [ ! -d "migrations" ]; then
  python manage.py db init
fi
python manage.py db migrate -m "`date '+%Y%m%d%H%M'`"
python manage.py db show
python manage.py db upgrade

gunicorn -b 127.0.0.1:4000 app:app \
--error-logfile "${ERROR_LOG}" \
--access-logfile "${ACCESS_LOG}" \
--timeout 300 \
--workers 4

deactivate

