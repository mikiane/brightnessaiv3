#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de veille automatique sur l'Intelligence Artificielle (v2)
Utilise le template unifié lib__auto_watch_template
"""

from libs.lib__auto_watch_template import create_ai_watch
from libs import lib__config as config


if __name__ == "__main__":
    # Créer et lancer le bot de veille IA
    bot = create_ai_watch()
    bot.run()


