if [ "$1" == "get" ]; then
  curl --cookie COOKIE --insecure -H "Content-Type: application/json" -X POST https://127.0.0.1:8580/user/get
fi
if [ "$1" == "setpassword" ]; then
    curl --cookie-jar COOKIE --insecure -H "Content-Type: application/json" -X POST -d '{"username": "aldwin", "password": "TesT34!@"}' https://127.0.0.1:8580/user/setpassword
fi
if [ "$1" == "setnewpassword" ]; then
  curl --cookie COOKIE --insecure -H "Content-Type: application/json" -X POST -d '{"old_password": "TesT34!@", "new_password": "TesT34!@"}' https://127.0.0.1:8580/user/setnewpassword
fi
if [ "$1" == "login" ]; then
  curl --cookie-jar COOKIE --insecure -H "Content-Type: application/json" -X POST -d '{"username": "aldwin", "password": "TesT34!@", "code2fa": "'$2'"}' https://127.0.0.1:8580/user/login
fi
if [ "$1" == "logout" ]; then
  curl --cookie COOKIE --insecure -H "Content-Type: application/json" -X POST https://127.0.0.1:8580/user/logout
fi
