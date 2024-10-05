#!/bin/python3
"""
Download certificates from FreeTSA
"""
import subprocess
import os

if not os.path.exists("freetsa"):
    os.mkdir("freetsa")

subprocess.run("curl -o freetsa/cacert.pem https://freetsa.org/files/cacert.pem", shell=True)
subprocess.run("curl -o freetsa/tsa.crt https://freetsa.org/files/tsa.crt", shell=True)
