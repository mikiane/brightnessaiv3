# -*- coding: utf-8 -*-
from libs.lib__llm_models import llm_manager

consigne = "Bonjour"
texte = "Explique-moi la différence entre CPU et GPU en 3 points."
model = "gpt-4"

for chunk in llm_manager.generate_chat(consigne, texte, model=model):
    print(chunk)