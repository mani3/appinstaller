#!/usr/bin/env bash

mkdir cer
cd cer
# for Mac OSX
ip=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | cut -d\  -f2)
#ip=$(ifconfig | grep 'inet addr:' | sed -e 's/^.*inet addr://' -e 's/ .*//')
echo $ip
openssl genrsa -out myself-server.key 2048
openssl req -new -key myself-server.key -out myself-server.cer -days 3650 -subj /CN=$ip
openssl x509 -in myself-server.cer -days 3650 -req -signkey myself-server.key -out server.crt
cp server.crt ../app/static/
