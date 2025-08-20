#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test d'envoi d'email HTML via Brevo en appelant
libs.lib__agent_buildchronical.mail_html(title, text, email)

Exemple d'utilisation:
  cd /home/michel/brightnessaiv3 && /home/michel/myenv/bin/python -m tests.test_send_email_brevo \
    --to "destinataire@example.com" \
    --subject "Test Brevo" \
    --html "<h3>Test</h3><p>Message de test</p>"
"""

import argparse
from libs import lib__config as config
from libs import lib__agent_buildchronical as chronical


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test d'envoi d'email HTML via Brevo")
    parser.add_argument("--to", required=True, help="Adresse e-mail destinataire")
    parser.add_argument("--subject", default="Test Brevo HTML", help="Sujet de l'email")
    parser.add_argument(
        "--html",
        default="<h3>Test</h3><p>Message de test envoyé depuis BrightnessAI v3.</p>",
        help="Contenu HTML du message",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if not getattr(config, "BREVO_API_KEY", None):
        config.logger.warning("BREVO_API_KEY manquante dans l'environnement (.env)")

    config.logger.info(
        f"Envoi d'un email HTML de test via Brevo → to={args.to}, subject={args.subject}"
    )
    chronical.mail_html(args.subject, args.html, args.to)
    config.logger.info("Demande d'envoi effectuée (voir logs Brevo pour le détail)")


if __name__ == "__main__":
    main()


