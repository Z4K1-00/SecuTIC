import subprocess
import os
from io import BytesIO
from PIL import Image

PRIVATE_KEY = "certs/ecc.server.key.pem"
PUBLIC_KEY = "certs/ecc.server.key.pub.pem"
ALGO = "sha256"


def getTSR(filename: str):
    """Get a TSR for the specified filename from freetsa.org. Command are from https://www.freetsa.org/index_en.php

    Args:
        filename (str): Filename of the file which want the TSR
    """

    # Create out folder
    if not os.path.exists("out"):
        os.mkdir("out")

    # Make a Time Stamp Request
    proc = subprocess.run(f"openssl ts -query -data '{filename}' -no_nonce -{ALGO} -cert -out out/file.tsq", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Request a Time Stamp Response
    proc = subprocess.run(f"curl -H 'Content-Type: application/timestamp-query' --data-binary '@out/file.tsq' https://freetsa.org/tsr > out/file.tsr", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Load file and return the Time Stamp Response
    with open("out/file.tsr", "rb") as f:
        return f.read()


def creation_contenu_cache(identite: str, intitule: str) -> bytes:
    """
    Créer le bloc avec le timestamp
    Args:
        identite: Identité
        intitule: Intitulé

    Returns:
        Le bloc sous forme: identité + padding de zéro + intitulé + timestamp
    """
    identite = identite.encode()
    intitule = intitule.encode()

    # Verify args lengths
    nb_zero = 64 - len(identite) - len(intitule)
    if nb_zero <= 1:
        raise ValueError("Taille identite et intitule trop grande (le total doit être inférieur ou égal à 63 octects)")
    
    # Create out folder
    if not os.path.exists("out"):
        os.mkdir("out")
    
    with open("out/data.tmp", "wb") as f:
        f.write(identite + b''.join([b"\0" for _ in range(nb_zero)]) + intitule)

    timestamp = getTSR("out/data.tmp")
    
    return identite + b''.join([b"\0" for _ in range(nb_zero)]) + intitule + timestamp


def verification_contenu_cache(contenu: bytes) -> bool:
    """
    Vérifie le contenu caché donné
    Args:
        contenu: contenu caché

    Returns:
        True si le contenu est valide, False sinon
    """
    timestamp = contenu[64:]

    # Create out folder
    if not os.path.exists("out"):
        os.mkdir("out")

    # Sauvegarde des données pour pouvoir les utiliser dans la commande suivante
    with open("out/data.tmp", "wb") as f:
        f.write(contenu[:64])

    # Create out folder and save timestamp
    if not os.path.exists("out"):
        os.mkdir("out")
    with open("out/tmp.tsr", "wb") as f:
        f.write(timestamp)

    proc = subprocess.run(f"openssl ts -verify -in out/tmp.tsr -data out/data.tmp -CAfile freetsa/cacert.pem -untrusted freetsa/tsa.crt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.stdout == b"Verification: OK\n"


def sign_data(data: bytes, key_filename: str) -> bytes:
    """
    Sign data with the key in the key_filename file
    Args:
        data: Data to sign
        key_filename: Filename of the key

    Returns:
        Signature of the data
    """
    proc = subprocess.Popen(f"openssl dgst -{ALGO} -sign {key_filename}", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    communication = proc.communicate(data)
    return communication[0]


def verification_sign_data(data: bytes, signature: bytes, key_filename: str) -> bool:
    """
    Verify the signature
    Args:
        data: Data of the signature
        signature: Signature
        key_filename: Filename of the key

    Returns:
        True if the signature is correct, False otherwise
    """
    # Create out folder
    if not os.path.exists("out"):
        os.mkdir("out")
    
    with open("out/sign.tmp", "wb") as f:
        f.write(signature)

    proc = subprocess.Popen(f"openssl dgst -{ALGO} -verify {key_filename} -signature out/sign.tmp", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    communication = proc.communicate(data)
    return communication[0] == b"Verified OK\n"
