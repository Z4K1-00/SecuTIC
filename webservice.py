#!/usr/bin/python3

from io import BytesIO
from bottle import route, request, response, run
from image import creation_certificat, recuperation_steganographie, recuperation_qrcode
from crypto import verification_sign_data, verification_contenu_cache, PUBLIC_KEY
from PIL import Image


@route('/certificat', method='POST')
def creation_attestation():
    """
    Create certificate route. Args identite and intitule_certif must be given
    """
    # Verify identity
    contenu_identite = request.forms.get('identite')
    if contenu_identite is None:
        return "Identite invalide"

    # Verify intitule
    contenu_intitule_certification = request.forms.get('intitule_certif')
    if contenu_intitule_certification is None:
        return "Intiutule invalide"

    attestation = creation_certificat(contenu_identite, contenu_intitule_certification)

    response.set_header('Content-Type', 'image/png')

    # Pour retourner une image de PIL depuis Bottle: https://stackoverflow.com/a/67809064
    membuf = BytesIO()
    attestation.save(membuf, format="png")
    return membuf.getvalue()


@route('/verification', method='POST')
def verification_attestation():
    """
    Create verification route. The certificate must be given in the argument image.
    """
    response.set_header('Content-type', 'text/plain')
    contenu_image = request.files.get('image')
    image_data = BytesIO()
    contenu_image.save(image_data, overwrite=True)
    image = Image.open(image_data)
    # image_data = BytesIO()
    # image.save(image_data, "png")

    signature = bytes.fromhex(recuperation_qrcode(image))
    steganographie = bytes.fromhex(recuperation_steganographie(image))

    if signature == b"" or steganographie == b"":
        return "Not OK"
    
    if not verification_sign_data(steganographie[:64], signature, PUBLIC_KEY):
        return "Not OK"

    if not verification_contenu_cache(steganographie):
        return "Not OK"

    return "OK"


if __name__ == "__main__":
    run(host='0.0.0.0', port=8080, debug=True)
