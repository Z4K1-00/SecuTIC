# HTTP (direct avec le serveur Python)

# Envoie données étudiant
curl -X POST -d 'identite=toto' -d 'intitule_certif=SecuTIC' http://localhost:8080/certificat -o cert.png

# Vérification avec image
curl -F image=@cert.png http://localhost:8080/verification


# HTTPS (avec le proxy)

# Envoie données étudiant
curl -X POST -d 'identite=toto' -d 'intitule_certif=SecuTIC' https://localhost:9000/certificat --cacert certs/ecc.ca.cert.pem -o cert.png

# Vérification avec image
curl -F image=@cert.png https://localhost:9000/verification --cacert certs/ecc.ca.cert.pem