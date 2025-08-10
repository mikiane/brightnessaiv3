#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de veille automatique pour Learning & Development
Utilise le template unifié lib__auto_watch_template
"""

from libs.lib__auto_watch_template import create_ld_watch
from libs import lib__config as config

if __name__ == "__main__":
    # Créer et lancer le bot de veille L&D
    bot = create_ld_watch()
    bot.run() 