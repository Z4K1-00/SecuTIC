#!/bin/bash

ALGO="prime256v1"

if [ ! -d certs ]; then
    echo "Folder certs doesn't exists !"
    exit 1
fi

cd certs

openssl ecparam -out ecc.ca.key.pem -name $ALGO -genkey
openssl req -batch -config root-ca.cnf -new -nodes -x509 -sha256 -key ecc.ca.key.pem -text -out ecc.ca.cert.pem
openssl ecparam -out ecc.server.key.pem -name $ALGO -genkey
openssl req -batch -config server-cert.cnf -new -sha256 -key ecc.server.key.pem -text | \
    openssl x509 -req -days 3650 -CA ecc.ca.cert.pem -CAkey ecc.ca.key.pem -CAcreateserial -text -out ecc.server.pem
cat ecc.server.key.pem ecc.server.pem > bundle_server.pem
openssl ec -in ecc.server.key.pem -pubout -out ecc.server.key.pub.pem