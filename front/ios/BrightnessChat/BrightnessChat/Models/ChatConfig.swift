//
//  ChatConfig.swift
//  BrightnessChat
//
//  Modèle de configuration du chat
//

import Foundation

struct ChatConfig: Codable {
    let title: String
    let logoUrl: String
    let apiUrl: String
    let searchUrl: String
    let apiKey: String
    let brainId: String
    let model: String
    let temperature: Double
    let withHistory: Bool
    let activateSource: Bool
    let system: String
    let consigne: String
    let initialisation: String?
    
    enum CodingKeys: String, CodingKey {
        case title, logoUrl, apiUrl, searchUrl, apiKey
        case brainId = "brain_id"
        case model, temperature
        case withHistory, system, consigne, initialisation
        case activateSource = "activate_source"
    }
    
    /// Charge la configuration depuis le bundle
    static func load(from filename: String) throws -> ChatConfig {
        print("🔍 Tentative de chargement de: \(filename).json")
        
        // Chercher d'abord dans Resources/
        if let url = Bundle.main.url(forResource: filename, withExtension: "json", subdirectory: "Resources") {
            print("✅ Fichier trouvé dans Resources/: \(url.path)")
            let data = try Data(contentsOf: url)
            let decoder = JSONDecoder()
            let config = try decoder.decode(ChatConfig.self, from: data)
            print("✅ Configuration chargée avec succès: \(config.title)")
            return config
        }
        
        // Sinon chercher à la racine
        if let url = Bundle.main.url(forResource: filename, withExtension: "json") {
            print("✅ Fichier trouvé à la racine: \(url.path)")
            let data = try Data(contentsOf: url)
            let decoder = JSONDecoder()
            let config = try decoder.decode(ChatConfig.self, from: data)
            print("✅ Configuration chargée avec succès: \(config.title)")
            return config
        }
        
        // Lister les ressources disponibles pour debug
        print("❌ Fichier non trouvé. Ressources disponibles:")
        if let resourcePath = Bundle.main.resourcePath {
            let resourceURL = URL(fileURLWithPath: resourcePath)
            if let contents = try? FileManager.default.contentsOfDirectory(at: resourceURL, includingPropertiesForKeys: nil) {
                contents.prefix(10).forEach { print("  - \($0.lastPathComponent)") }
            }
        }
        
        throw ConfigError.fileNotFound(filename)
    }
}

enum ConfigError: LocalizedError {
    case fileNotFound(String)
    
    var errorDescription: String? {
        switch self {
        case .fileNotFound(let filename):
            return "Fichier de configuration non trouvé: \(filename).json"
        }
    }
}

