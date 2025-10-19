//
//  ChatService.swift
//  BrightnessChat
//
//  Service API pour les appels réseau
//

import Foundation

class ChatService {
    private let config: ChatConfig
    
    init(config: ChatConfig) {
        self.config = config
    }
    
    /// Recherche de contexte RAG
    func fetchContext(for query: String) async throws -> String {
        var request = URLRequest(url: URL(string: config.searchUrl)!)
        request.httpMethod = "POST"
        
        // Création du multipart/form-data
        let boundary = "Boundary-\(UUID().uuidString)"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        request.setValue(config.apiKey, forHTTPHeaderField: "X-API-Key")
        
        var body = Data()
        
        // Ajouter les champs
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"request\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(query)\r\n".data(using: .utf8)!)
        
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"brain_id\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(config.brainId)\r\n".data(using: .utf8)!)
        
        if !config.model.isEmpty {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"model\"\r\n\r\n".data(using: .utf8)!)
            body.append("\(config.model)\r\n".data(using: .utf8)!)
        }
        
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        request.httpBody = body
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw ChatError.searchFailed
        }
        
        // Parse JSON response
        if let json = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]],
           let firstResult = json.first,
           let answer = firstResult["answer"] as? String {
            return answer
        }
        
        return ""
    }
    
    /// Envoi d'une question au LLM avec streaming
    func sendToLLM(question: String, context: String, history: [Message]) async throws -> AsyncThrowingStream<String, Error> {
        var request = URLRequest(url: URL(string: config.apiUrl)!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("text/plain", forHTTPHeaderField: "Accept")
        request.setValue(config.apiKey, forHTTPHeaderField: "X-API-Key")
        
        // Construire la consigne contextuelle
        let contextualConsigne = buildConsigne(baseConsigne: config.consigne, history: history, context: context)
        
        let payload: [String: Any] = [
            "consigne": contextualConsigne.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? contextualConsigne,
            "texte": question.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? question,
            "system": config.system,
            "model": config.model,
            "temperature": String(format: "%.2f", config.temperature)
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        
        let (bytes, response) = try await URLSession.shared.bytes(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw ChatError.llmFailed
        }
        
        return AsyncThrowingStream { continuation in
            Task {
                do {
                    var buffer = Data()
                    for try await byte in bytes {
                        buffer.append(byte)
                        
                        // Essayer de décoder le buffer en UTF-8
                        if let text = String(data: buffer, encoding: .utf8) {
                            // Décodage réussi, envoyer le texte
                            continuation.yield(text)
                            buffer.removeAll()
                        }
                        // Si le décodage échoue, continuer d'accumuler les bytes
                        // (probablement au milieu d'un caractère multi-octets)
                    }
                    
                    // Envoyer les derniers bytes s'il en reste
                    if !buffer.isEmpty, let text = String(data: buffer, encoding: .utf8) {
                        continuation.yield(text)
                    }
                    
                    continuation.finish()
                } catch {
                    continuation.finish(throwing: error)
                }
            }
        }
    }
    
    private func buildConsigne(baseConsigne: String, history: [Message], context: String) -> String {
        var consigne = baseConsigne
        
        // Ajouter l'historique si activé
        if config.withHistory && !history.isEmpty {
            let lastMessages = history.suffix(4)
            let historyText = lastMessages.map { "- \($0.role.rawValue): \($0.content)" }.joined(separator: "\n")
            consigne += "\n\nContexte conversationnel:\n\(historyText)"
        }
        
        // Ajouter le contexte RAG
        if !context.isEmpty {
            consigne += "\n\nVoici un contexte à prendre en compte <<<Contexte>>>\n\(context)"
        }
        
        return consigne.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

enum ChatError: LocalizedError {
    case searchFailed
    case llmFailed
    
    var errorDescription: String? {
        switch self {
        case .searchFailed:
            return "Échec de la recherche de contexte"
        case .llmFailed:
            return "Échec de la communication avec le LLM"
        }
    }
}

