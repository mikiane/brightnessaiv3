#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import mimetypes
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException as BrevoApiException
from libs import lib__config as config
logger = config.logger


def mailfile(filename=None, destinataire='michel@brightness.fr', message=""):
    """
    Fonction pour envoyer un e-mail avec ou sans pièce jointe via Brevo (transactionnel).
    Ancien envoi SendGrid conservé en commentaire pour référence.
    
    Args:
        filename (str): Le chemin vers le fichier à joindre (optionnel).
        destinataire (str): Adresse e-mail du destinataire.
        message (str): Contenu texte à inclure dans le message.
    """
    
    # --- Ancien envoi SendGrid (conservé en commentaire) ---
    # from sendgrid import SendGridAPIClient
    # from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
    # message_mail = Mail(
    #     from_email='contact@brightness.fr',
    #     to_emails=destinataire,
    #     subject='Le résultat du traitement',
    #     plain_text_content='Votre demande a été traité.' + str(message)
    # )
    # if filename:
    #     with open(filename, 'rb') as f:
    #         data = f.read()
    #     encoded = base64.b64encode(data).decode()
    #     mime_type = mimetypes.guess_type(filename)[0]
    #     attachedFile = Attachment(FileContent(encoded), FileName(filename), FileType(mime_type), Disposition('attachment'))
    #     message_mail.attachment = attachedFile
    # try:
    #     sg = SendGridAPIClient(config.SENDGRID_KEY)
    #     response = sg.send(message_mail)
    #     logger.info(f"Email envoyé: {destinataire} - {filename} - {message}")
    #     logger.debug(f"Sendgrid status: {response.status_code}")
    # except Exception as e:
    #     logger.error(f"Erreur envoi email: {e}")
    
    # --- Nouvel envoi via Brevo TransactionalEmailsApi ---
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = config.BREVO_API_KEY
    api_client = sib_api_v3_sdk.ApiClient(configuration)
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(api_client)
    
    # Préparer le contenu du message
    text_content = 'Votre demande a été traitée. ' + str(message)
    
    # Construire l'objet email de base
    email_params = {
        "to": [{"email": destinataire}],
        "bcc": [{"email": "contact@mikiane.com"}],
        "sender": {"name": "Brightness.ai", "email": "contact@brightness.fr"},
        "subject": "Le résultat du traitement",
        "text_content": text_content
    }
    
    # Ajouter la pièce jointe si un fichier est fourni
    if filename:
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            encoded = base64.b64encode(data).decode()
            
            attachment = [{
                "name": os.path.basename(filename),
                "content": encoded
                # "contentType": mimetypes.guess_type(filename)[0] or 'application/octet-stream'  # optionnel
            }]
            email_params["attachment"] = attachment
        except Exception as e:
            logger.error(f"Erreur lecture du fichier '{filename}': {e}")
            return
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(**email_params)
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Email envoyé via Brevo: {destinataire} - {filename} - {message}")
        logger.debug(f"Brevo response: {api_response}")
    except BrevoApiException as e:
        logger.error(f"Erreur envoi email (Brevo): {e}")

    
    
