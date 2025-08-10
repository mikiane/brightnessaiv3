#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
import mimetypes
from libs import lib__config as config
logger = config.logger


def mailfile(filename=None, destinataire='michel@brightness.fr', message=""):
    message_mail = Mail(
        from_email='contact@brightness.fr',
        to_emails=destinataire,
        subject='Le résultat du traitement',
        plain_text_content='Votre demande a été traité.' + str(message)
    )
    
    if filename:
        with open(filename, 'rb') as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        mime_type = mimetypes.guess_type(filename)[0]
        attachedFile = Attachment(FileContent(encoded), FileName(filename), FileType(mime_type), Disposition('attachment'))
        message_mail.attachment = attachedFile

    try:
        sg = SendGridAPIClient(config.SENDGRID_KEY)
        response = sg.send(message_mail)
        logger.info(f"Email envoyé: {destinataire} - {filename} - {message}")
        logger.debug(f"Sendgrid status: {response.status_code}")
    except Exception as e:
        logger.error(f"Erreur envoi email: {e}")

    
    
