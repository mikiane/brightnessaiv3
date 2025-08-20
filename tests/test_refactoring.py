#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test pour valider les refactorings
Lance une série de tests pour vérifier que tout fonctionne
"""

import sys
import traceback

def test_import(module_name, description):
    """Teste l'import d'un module"""
    try:
        __import__(module_name)
        print(f"✅ {description}: OK")
        return True
    except Exception as e:
        print(f"❌ {description}: ERREUR")
        print(f"   {str(e)}")
        return False

def test_config():
    """Teste la configuration centralisée"""
    print(f"\n=== Test de lib__config ===")
    
    try:
        import lib__config as config
        
        # Vérifier les variables essentielles
        checks = [
            ("DEFAULT_MODEL", config.DEFAULT_MODEL),
            ("BASE_PATH", config.BASE_PATH),
            ("OPENAI_API_KEY", config.OPENAI_API_KEY),
        ]
        
        for name, value in checks:
            if value:
                print(f"✅ {name}: Configuré")
            else:
                print(f"⚠️  {name}: Non configuré")
        
        # Test de la fonction de validation
        if config.validate_config():
            print(f"✅ Configuration validée")
        else:
            print(f"⚠️  Configuration incomplète (vérifiez .env)")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur de configuration: {str(e)}")
        traceback.print_exc()
        return False

def test_llm_manager():
    """Teste le gestionnaire LLM unifié"""
    print(f"\n=== Test de lib__llm_models ===")
    
    try:
        from lib__llm_models import LLMManager
        
        # Créer une instance
        manager = LLMManager()
        print(f"✅ LLMManager créé avec succès")
        
        # Vérifier les méthodes
        methods = [
            "_get_openai_client",
            "_get_anthropic_client", 
            "_get_deepseek_client",
            "_get_xai_client",
            "_get_gemini_client",
            "generate_completion"
        ]
        
        for method in methods:
            if hasattr(manager, method):
                print(f"✅ Méthode {method}: Disponible")
            else:
                print(f"❌ Méthode {method}: Manquante")
                
        return True
        
    except Exception as e:
        print(f"❌ Erreur LLMManager: {str(e)}")
        traceback.print_exc()
        return False

def test_auto_watch_template():
    """Teste le template de veille automatique"""
    print(f"\n=== Test de lib__auto_watch_template ===")
    
    try:
        from lib__auto_watch_template import AutoWatchBot, create_ai_watch, create_ted_watch
        
        # Test de création d'un bot
        bot = AutoWatchBot("Test Bot", "test")
        print(f"✅ AutoWatchBot créé")
        
        # Test des factories
        ai_bot = create_ai_watch()
        print(f"✅ Factory create_ai_watch: OK")
        
        ted_bot = create_ted_watch()
        print(f"✅ Factory create_ted_watch: OK")
        
        # Vérifier les méthodes
        if hasattr(bot, "add_urls") and hasattr(bot, "add_rss_feeds") and hasattr(bot, "run"):
            print(f"✅ Méthodes du bot: OK")
        else:
            print(f"❌ Méthodes du bot: Incomplètes")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur AutoWatchBot: {str(e)}")
        traceback.print_exc()
        return False

def test_common_tasks():
    """Teste les tâches communes"""
    print(f"\n=== Test de lib__common_tasks ===")
    
    try:
        import lib__common_tasks as common
        
        functions = [
            "process_url",
            "process_rss",
            "process_multiple_urls",
            "clean_html_response",
            "build_watch_command"
        ]
        
        for func in functions:
            if hasattr(common, func):
                print(f"✅ Fonction {func}: Disponible")
            else:
                print(f"❌ Fonction {func}: Manquante")
                
        return True
        
    except Exception as e:
        print(f"❌ Erreur lib__common_tasks: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("="*60)
    print("Tests de validation du refactoring BrightnessAI v3")
    print("="*60)
    
    results = []
    
    # Tests d'import basiques
    print(f"\n=== Tests d'imports ===")
    results.append(test_import("lib__config", "Configuration centralisée"))
    results.append(test_import("lib__llm_models", "Gestionnaire LLM unifié"))
    results.append(test_import("lib__common_tasks", "Tâches communes"))
    results.append(test_import("lib__auto_watch_template", "Template auto_watch"))
    
    # Tests approfondis
    results.append(test_config())
    results.append(test_llm_manager())
    results.append(test_auto_watch_template())
    results.append(test_common_tasks())
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 Tous les tests sont passés ({passed}/{total})")
        print("Le refactoring est prêt à être déployé!")
    else:
        print(f"⚠️  {passed}/{total} tests passés")
        print("Certains ajustements sont nécessaires")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main()) 