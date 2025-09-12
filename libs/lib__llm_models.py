# -*- coding: utf-8 -*-
"""
Librairie unifiée pour la gestion des modèles LLM
Centralise tous les appels aux différents LLMs (OpenAI, Anthropic, Deepseek, Grok, Google, etc.)
"""

import openai
from openai import OpenAI
import anthropic
from huggingface_hub import InferenceClient
from typing import Generator, Optional, Union
from libs import lib__config as config
from libs import lib__anthropic
import logging
from math import ceil

# Configuration du logger
logger = config.logger


def extract_context(text, model):
    """
    Extraire un contexte de 'text' basé sur la limite spécifiée.

    Si la longueur de 'text' est inférieure à 'limit', renvoie le texte complet.
    Sinon, renvoie une combinaison des premiers et derniers caractères de 'text'
    avec ' [...] ' inséré au milieu pour indiquer la coupure.

    :param text: La chaîne de caractères à traiter.
    :param model: Le modèle pour déterminer la limite de tokens.
    :return: La chaîne de caractères traitée.
    """
    token_nb = 10000
    if model == "gpt-4.5-preview":
        token_nb = 128000
    if model == "claude-2" or model == "claude-2.1":
        token_nb = 100000 
    if model == "claude-3" or model == "claude-3-opus-20240229":
        token_nb = 100000 
    if model == "gpt-4":
        token_nb = 8000
    if model == "gpt-4-turbo-preview" or model == "gpt-4-turbo":
        token_nb = 128000
    if model == config.DEFAULT_MODEL:
        token_nb = 250000
    if model == "gpt-3.5-turbo-16k": 
        token_nb = 16000
    if model == "hf":
        token_nb = 2000  
    if model == "mistral":
        token_nb = 2000      
    
    if token_nb > 2000:
        limit = (int(token_nb)*2) - 4000
    else:
        limit = int((int(token_nb)*2)/2)
    
    if len(text) < limit:
        return text
    else:
        half_limit_adjusted = limit // 2 - 4
        return text[:half_limit_adjusted] + ' [...] ' + text[-half_limit_adjusted:]


class LLMManager:
    """Gestionnaire unifié pour tous les modèles LLM"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.deepseek_client = None
        self.xai_client = None
        self.gemini_client = None
        self.hf_client = None
        
    def _get_openai_client(self):
        """Initialise le client OpenAI de manière lazy"""
        if not self.openai_client:
            self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        return self.openai_client
    
    def _get_anthropic_client(self):
        """Initialise le client Anthropic de manière lazy"""
        if not self.anthropic_client:
            self.anthropic_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        return self.anthropic_client
    
    def _get_deepseek_client(self):
        """Initialise le client Deepseek de manière lazy"""
        if not self.deepseek_client:
            self.deepseek_client = OpenAI(
                api_key=config.DEEPSEEK_KEY,
                base_url="https://api.deepseek.com"
            )
        return self.deepseek_client
    
    def _get_xai_client(self):
        """Initialise le client XAI/Grok de manière lazy"""
        if not self.xai_client:
            self.xai_client = OpenAI(
                api_key=config.XAI_KEY,
                base_url="https://api.x.ai/v1"
            )
        return self.xai_client
    
    def _get_gemini_client(self):
        """Initialise le client Google Gemini de manière lazy"""
        if not self.gemini_client:
            try:
                import google.generativeai as genai
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.gemini_client = genai
            except ImportError:
                logger.error("Google Generative AI library not installed. Run: pip install google-generativeai")
                raise
        return self.gemini_client
    
    def _get_huggingface_client(self):
        """Initialise le client HuggingFace de manière lazy"""
        if not self.hf_client:
            self.hf_client = InferenceClient(
                config.MODEL_URL,
                token=config.HF_API_TOKEN
            )
        return self.hf_client
    
    def generate_completion(
        self,
        prompt: str,
        context: str = "",
        input_data: str = "",
        model: str = None,
        max_tokens: int = 10000,
        temperature: float = 0.2,
        stream: bool = True,
        system: str = ""
    ) -> Generator[str, None, None]:
        """Génère une complétion avec le modèle spécifié"""
        
        # Utiliser le modèle par défaut si aucun n'est spécifié
        if not model:
            model = config.DEFAULT_MODEL
            
        # Construction du prompt complet
        if context and input_data:
            full_prompt = f"Context: {context}\n{input_data}\nQuery: {prompt}"
        elif input_data:
            full_prompt = f"{input_data}\n{prompt}"
        else:
            full_prompt = prompt
        
        # Routage vers le bon modèle
        if "gpt" in model.lower() or "o1" in model.lower():
            return self._generate_openai(full_prompt, model, max_tokens, temperature, stream, system)
        elif "claude" in model.lower():
            return self._generate_anthropic(full_prompt, model, max_tokens, temperature, stream)
        elif "deepseek" in model.lower():
            return self._generate_deepseek(full_prompt, max_tokens, temperature, stream)
        elif "grok" in model.lower() or "xai" in model.lower():
            return self._generate_grok(full_prompt, model, max_tokens, temperature, stream)
        elif "gemini" in model.lower():
            return self._generate_gemini(full_prompt, model, max_tokens, temperature, stream)
        elif model == "hf":
            return self._generate_huggingface(full_prompt, max_tokens, temperature, stream)
        else:
            # Par défaut, utilise OpenAI
            return self._generate_openai(full_prompt, model, max_tokens, temperature, stream, system)
    
    def _generate_openai(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        stream: bool,
        system: str = ""
    ) -> Generator[str, None, None]:
        """Génère une complétion avec OpenAI"""
        try:
            client = self._get_openai_client()
            # Route les modèles récents (gpt-5*) vers l'API Responses (pas de max_tokens)
            if str(model).lower().startswith("gpt-5"):
                # Prépare l'input au format Responses
                input_msgs = []
                if system:
                    input_msgs.append({
                        "role": "developer",
                        "content": [{"type": "input_text", "text": system}]
                    })
                input_msgs.append({
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}]
                })

                # Appel non-streaming (plus fiable); on simulera le streaming côté serveur
                resp = client.responses.create(
                    model=model,
                    input=input_msgs,
                    # Ne pas passer max_tokens: certains modèles exigent max_completion_tokens / max_output_tokens
                    # temperature peut être ignorée par certains modèles reasoning
                    temperature=temperature if temperature is not None else 0.2,
                )

                # Extraction robuste du texte
                def _extract_response_text(r):
                    try:
                        t = getattr(r, "output_text", None)
                        if isinstance(t, str) and t.strip():
                            return t
                    except Exception:
                        pass
                    try:
                        out = getattr(r, "output", None)
                        if isinstance(out, list):
                            parts = []
                            for item in out:
                                content = item.get("content") if isinstance(item, dict) else getattr(item, "content", None)
                                if isinstance(content, list):
                                    for c in content:
                                        tt = c.get("text") if isinstance(c, dict) else getattr(c, "text", None)
                                        if isinstance(tt, str) and tt:
                                            parts.append(tt)
                            if parts:
                                return "\n".join(parts)
                    except Exception:
                        pass
                    try:
                        t2 = getattr(r, "text", None)
                        if isinstance(t2, str) and t2.strip():
                            return t2
                    except Exception:
                        pass
                    try:
                        return str(r)
                    except Exception:
                        return ""

                text = _extract_response_text(resp)
                if not stream:
                    yield text
                else:
                    # Streaming simulé en petits blocs pour compatibilité SSE
                    chunk_size = 200
                    for i in range(0, len(text), chunk_size):
                        yield text[i:i+chunk_size]
                return
            
            # Cas spéciaux pour certains modèles
            if model in ["o1-preview", "o1", "o3-mini"]:
                messages = [{"role": "user", "content": system + "\n" + prompt if system else prompt}]
            else:
                messages = [
                    {"role": "system", "content": system or "Je suis un assistant parlant parfaitement le français et l'anglais."},
                    {"role": "user", "content": prompt}
                ]
            
            # Certains modèles (famille o1/o3) exigent 'max_completion_tokens'
            mlow = str(model).lower()
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream,
            }
            if mlow.startswith("o1") or mlow.startswith("o3"):
                params["max_completion_tokens"] = max_tokens
            else:
                params["max_tokens"] = max_tokens

            completion = client.chat.completions.create(**params)
            
            if stream:
                for message in completion:
                    if message.choices[0].delta.content:
                        yield message.choices[0].delta.content
            else:
                yield completion.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Erreur avec OpenAI: {str(e)}")
            raise
    
    def _generate_anthropic(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        stream: bool
    ) -> Generator[str, None, None]:
        """Génère une complétion avec Anthropic"""
        try:
            # Utilise la librairie existante pour Anthropic
            response = lib__anthropic.generate_chat_completion_anthropic(
                consigne="",
                texte=prompt,
                model=model,
                temperature=temperature
            )
            for content in response:
                yield content
                
        except Exception as e:
            logger.error(f"Erreur avec Anthropic: {str(e)}")
            raise
    
    def _generate_deepseek(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        stream: bool
    ) -> Generator[str, None, None]:
        """Génère une complétion avec Deepseek"""
        try:
            client = self._get_deepseek_client()
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Je suis un assistant parlant parfaitement le français et l'anglais."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                for message in response:
                    if message.choices[0].delta.content:
                        yield message.choices[0].delta.content
            else:
                content = response.choices[0].message.content
                # Simuler un stream caractère par caractère
                for char in content:
                    yield char
                    
        except Exception as e:
            logger.error(f"Erreur avec Deepseek: {str(e)}")
            raise
    
    def _generate_grok(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        stream: bool
    ) -> Generator[str, None, None]:
        """Génère une complétion avec Grok/XAI"""
        try:
            client = self._get_xai_client()
            
            response = client.chat.completions.create(
                model=model or "grok-2-latest",
                messages=[
                    {"role": "system", "content": "Tu es Grok 2, le modèle de langage d'IA frontière de xAI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                for message in response:
                    if message.choices[0].delta.content:
                        yield message.choices[0].delta.content
            else:
                content = response.choices[0].message.content
                for char in content:
                    yield char
                    
        except Exception as e:
            logger.error(f"Erreur avec Grok: {str(e)}")
            raise
    
    def _generate_gemini(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        stream: bool
    ) -> Generator[str, None, None]:
        """Génère une complétion avec Google Gemini"""
        try:
            genai = self._get_gemini_client()
            
            # Configuration du modèle
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": max_tokens,
                "response_mime_type": "text/plain",
            }
            
            gemini_model = genai.GenerativeModel(
                model_name=model or "gemini-2.0-flash-thinking-exp-1219",
                generation_config=generation_config,
            )
            
            # Démarrer une session de chat
            chat_session = gemini_model.start_chat(history=[])
            
            # Envoyer le message
            response = chat_session.send_message(prompt, stream=stream)
            
            if stream:
                for chunk in response:
                    if hasattr(chunk, 'text'):
                        yield chunk.text
            else:
                # Simuler un stream pour Gemini qui ne supporte pas nativement
                full_text = response.text
                chunk_size = 100
                total_chunks = ceil(len(full_text) / chunk_size)
                
                for i in range(total_chunks):
                    start_idx = i * chunk_size
                    end_idx = min((i + 1) * chunk_size, len(full_text))
                    chunk = full_text[start_idx:end_idx]
                    yield chunk
                
        except Exception as e:
            logger.error(f"Erreur avec Gemini: {str(e)}")
            raise

    def extract_context(self, text, model):
        """
        Extraire un contexte de 'text' basé sur la limite spécifiée.
        
        Si la longueur de 'text' est inférieure à 'limit', renvoie le texte complet.
        Sinon, renvoie une combinaison des premiers et derniers caractères de 'text'
        avec ' [...] ' inséré au milieu pour indiquer la coupure.
        
        :param text: La chaîne de caractères à traiter.
        :param model: Le modèle utilisé pour déterminer la limite.
        :return: La chaîne de caractères traitée.
        """
        token_nb = 10000
        if model == "gpt-4.5-preview":
            token_nb = 128000
        if model == "claude-2" or model == "claude-2.1":
            token_nb = 100000 
        if model == "claude-3" or model == "claude-3-opus-20240229" or model == "claude-3-5-sonnet-20241022":
            token_nb = 100000 
        if model == "gpt-4":
            token_nb = 8000
        if model == "gpt-4-turbo-preview" or model == "gpt-4-turbo":
            token_nb = 128000
        if model == config.DEFAULT_MODEL:
            token_nb = 250000
        if model == "gpt-3.5-turbo-16k": 
            token_nb = 16000
        if model == "hf":
            token_nb = 2000  
        if model == "mistral":
            token_nb = 2000
        if model == "google" or "gemini" in str(model).lower():
            token_nb = 30000
        if model == "grok" or "xai" in str(model).lower():
            token_nb = 100000
        if model == "deepseek":
            token_nb = 16000
        
        if token_nb > 2000:
            limit = (int(token_nb)*2) - 4000
        else:
            limit = int((int(token_nb)*2)/2)
        
        if len(text) < limit:
            return text
        else:
            half_limit_adjusted = limit // 2 - 4
            return text[:half_limit_adjusted] + ' [...] ' + text[-half_limit_adjusted:]

    def generate_chat(self, consigne, texte, system="", model=None, temperature=0.2):
        """
        Méthode de compatibilité avec l'ancienne API generatechatcompletion.generate_chat
        
        Args:
            consigne: L'instruction ou question
            texte: Le texte/contexte à traiter
            system: Le message système (optionnel)
            model: Le modèle à utiliser
            temperature: La température pour la génération
            
        Yields:
            str: Les chunks de texte générés
        """
        # Utiliser le modèle par défaut si aucun n'est spécifié
        if not model:
            model = config.DEFAULT_MODEL
            
        # Extraire le contexte selon le modèle
        texte = self.extract_context(texte, model)
        
        # Construire le prompt complet
        prompt = f"{consigne} : {texte}" if consigne and texte else consigne or texte
        
        # Log pour debug
        logger.info(f"generate_chat called with model: {model}, temperature: {temperature}")
        
        # Gérer les cas spéciaux de modèles
        if model == "claude-2":
            model = "claude-2.1"
        elif model == "claude-3":
            model = "claude-3-opus-20240229"
        elif model == "google":
            model = "gemini-2.0-flash-thinking-exp-1219"
        elif model == "grok":
            model = "grok-2-latest"
        elif model == "deepseek":
            model = "deepseek-chat"
            
        # Cas spécial pour HuggingFace
        if model == "hf":
            yield from self._generate_hf(prompt, temperature)
        else:
            # Utiliser la méthode generate_completion existante
            yield from self.generate_completion(
                prompt="",
                context="",
                input_data=prompt,
                model=model,
                max_tokens=10000,
                temperature=temperature,
                stream=True,
                system=system
            )
    
    def _generate_hf(self, prompt, temperature=0.2):
        """Génère une complétion avec HuggingFace"""
        try:
            if not self.hf_client:
                from huggingface_hub import InferenceClient
                self.hf_client = InferenceClient(
                    config.MODEL_URL, 
                    token=config.HF_API_TOKEN
                )
            
            # Format du prompt pour HuggingFace
            prompt_hf = f"<s>[INST]{prompt}[/INST]"
            
            response = self.hf_client.text_generation(
                prompt_hf,
                max_new_tokens=1024,
                temperature=temperature,
                stream=True
            )
            
            for chunk in response:
                yield chunk
                
        except Exception as e:
            logger.error(f"Erreur avec HuggingFace: {str(e)}")
            raise


# Instance singleton du gestionnaire LLM
llm_manager = LLMManager()

# Fonction de compatibilité pour l'ancienne API
def generate_chat(consigne, texte, system="", model=None, temperature=0):
    """
    Fonction de compatibilité avec generatechatcompletion.generate_chat
    """
    return llm_manager.generate_chat(consigne, texte, system, model, temperature)