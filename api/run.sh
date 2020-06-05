#!/bin/bash

source parse_config.sh
eval $(parse_yaml config.conf "config_")
VIRTENV=/tmp/virtualenv/${config_virtualenv_dir}/${config_virtualenv_name}
if [ ! -d ${VIRTENV} ]; then
    ./install_env.sh
fi

mkdir -p log
let NUM_WORKERS=$(grep -c ^processor /proc/cpuinfo)*2+1
source ${VIRTENV}/bin/activate
#rm log/*; touch log/exceptions.log
NAME="${config_virtualenv_dir}_api"
gunicorn --timeout 180 --reload -b ${config_socket_bind}:${config_socket_port} --certfile=server.crt --keyfile=server.key -w ${NUM_WORKERS} --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(D)s "%(f)s" "%(a)s"' --access-logfile log/access_gunicorn.log --error-logfile log/error_gunicorn.log --log-level normal --capture-output --name ${NAME} ws:App
deactivate

#remote_address - user_name date_of_the_request "status_line" status(200) length microsec "referer" "user_agent"
#Identifier     Description
#h     remote address
#l     '-'
#u     user name
#t     date of the request
#r     status line (e.g. GET / HTTP/1.1)
#m     request method
#U     URL path without query string
#q     query string
#H     protocol
#s     status
#B     response length
#b     response length or '-' (CLF format)
#f     referer
#a     user agent
#T     request time in seconds
#D     request time in microseconds
#L     request time in decimal seconds
#p     process ID
#{Header}i     request header
#{Header}o     response header
#{Variable}e     environment variable
