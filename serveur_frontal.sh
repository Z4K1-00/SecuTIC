#!/bin/bash

ss -tlnp | grep 0.0.0.0:8080 > /dev/null
if [ $? -ne 0 ]; then
    echo "Please start Python server before this"
    exit 1
fi

socat openssl-listen:9000,fork,cert=certs/bundle_server.pem,cafile=certs/ecc.ca.cert.pem,verify=0 tcp:127.0.0.1:8080