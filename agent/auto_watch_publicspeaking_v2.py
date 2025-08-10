#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de veille automatique pour Public Speaking
Utilise le template unifié lib__auto_watch_template
"""

from libs.lib__auto_watch_template import create_publicspeaking_watch
from libs import lib__config as config

if __name__ == "__main__":
    # Créer et lancer le bot de veille Public Speaking
    bot = create_publicspeaking_watch()
    bot.run() 