//
//  ChatViewModel.swift
//  BrightnessChat
//
//  ViewModel principal du chat
//

import Foundation
import SwiftUI

@MainActor
class ChatViewModel: ObservableObject {
    @Published var messages: [Message] = []
    @Published var config: ChatConfig?
    @Published var isLoading = true  // Commencer en mode chargement
    @Published var isSending = false
    @Published var errorMessage: String?
    @Published var statusText = ""
    
    private var chatService: ChatService?
    private var currentTask: Task<Void, Never>?
    
    init() {
        // Charger de manière asynchrone pour ne pas bloquer l'UI
        Task {
            await loadConfiguration()
        }
    }
    
    func loadConfiguration() async {
        do {
            let loadedConfig = try ChatConfig.load(from: AppConfig.defaultConfigFile)
            self.config = loadedConfig
            self.chatService = ChatService(config: loadedConfig)
            
            // Ajouter le message d'initialisation si présent
            if let initialisation = loadedConfig.initialisation, !initialisation.isEmpty {
                let initMessage = Message(role: .assistant, content: initialisation)
                messages.append(initMessage)
            }
            
            isLoading = false  // Chargement terminé
        } catch {
            self.errorMessage = "Erreur de chargement de la configuration: \(error.localizedDescription)"
            isLoading = false
        }
    }
    
    func sendMessage(_ text: String) {
        guard let config = config, let chatService = chatService else { return }
        guard !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        
        // Ajouter le message utilisateur
        let userMessage = Message(role: .user, content: text)
        messages.append(userMessage)
        
        // Créer un message assistant vide
        let assistantMessage = Message(role: .assistant, content: "")
        messages.append(assistantMessage)
        let assistantIndex = messages.count - 1
        
        isSending = true
        statusText = "L'IA réfléchit..."
        
        currentTask = Task {
            do {
                // 1. Récupérer le contexte
                let context = try await chatService.fetchContext(for: text)
                
                // 2. Envoyer au LLM et streamer la réponse
                let history = messages.dropLast().filter { $0.role != .system }
                let stream = try await chatService.sendToLLM(
                    question: text,
                    context: context,
                    history: Array(history)
                )
                
                var fullContent = ""
                
                for try await chunk in stream {
                    fullContent += chunk
                    messages[assistantIndex].content = fullContent
                }
                
                isSending = false
                statusText = ""
                
            } catch {
                messages[assistantIndex].content = "[Erreur] \(error.localizedDescription)"
                isSending = false
                statusText = ""
                errorMessage = error.localizedDescription
            }
        }
    }
    
    func stopGeneration() {
        currentTask?.cancel()
        currentTask = nil
        isSending = false
        statusText = ""
    }
}

