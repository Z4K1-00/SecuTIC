import subprocess
import os
import qrcode
from PIL import Image
import steganographie
import zbarlight
from crypto import creation_contenu_cache, sign_data, PRIVATE_KEY


def creation_certificat(identite: str, intitule: str) -> Image:
    """
    Créer le certificat
    Args:
        identite: Identité
        intitule: Intitulé

    Returns:
        Le certificat
    """
    # Create out folder
    if not os.path.exists("out"):
        os.mkdir("out")

    # Intégration identité et intitulé à l'attestation
    proc = subprocess.run(f'convert -size 1000x600 -gravity center -pointsize 56 label:"{intitule}\ndélivrée à {identite}" -transparent white out/texte.png', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc = subprocess.run(f'composite -gravity center out/texte.png fond_attestation.png out/attestation.png', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Signature avec clé privée
    nb_zero = 64 - len(identite.encode()) - len(intitule.encode())
    if nb_zero <= 1:
        raise ValueError("Taille identite et intitule trop grande")
    bloc = identite.encode() + b''.join([b"\0" for _ in range(nb_zero)]) + intitule.encode()
    signature = sign_data(bloc, PRIVATE_KEY)

    # Transforme la signature en format hex
    signature = signature.hex()

    # Création du QRCode
    qrCode = qrcode.make(signature)
    qrCode.save("out/qrCodetmp.png", scale=2)
    proc = subprocess.run(f"mogrify -resize 210x210 out/qrCodetmp.png", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Intégration du QRCode
    proc = subprocess.run(f"composite -geometry +1418+934 out/qrCodetmp.png out/attestation.png out/attestation.png", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Création du bloc
    bloc = creation_contenu_cache(identite, intitule)

    # Stéganographie du bloc
    attestation = Image.open("out/attestation.png")
    steganographie.cacher(attestation, bloc.hex())

    return attestation


def recuperation_steganographie(certificat: Image) -> str:
    """
    Récupère le contenu caché par stéganographie dans le certificat
    Args:
        certificat: Certificat

    Returns:
        Le contenu caché
    """
    return steganographie.recuperer(certificat, 11052)


def recuperation_qrcode(certificat: Image) -> str:
    """
    Récupère le contenu dans le QRCode du certificat
    Args:
        certificat: Certificat

    Returns:
        Le contenu dans le QRCode
    """
    qrImage = certificat.crop((1418, 934, 1418 + 210, 934 + 210))
    return zbarlight.scan_codes(['qrcode'], qrImage)[0].decode()
