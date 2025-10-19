//
//  UsageManager.swift
//  BrightnessChat
//
//  Gestion du compteur de requêtes gratuites
//

import Foundation

@MainActor
class UsageManager: ObservableObject {
    @Published var requestCount: Int = 0
    
    private let userDefaults = UserDefaults.standard
    private let requestCountKey = "brightness_request_count"
    private let lastResetDateKey = "brightness_last_reset_date"
    
    static let freeRequestLimit = 5
    
    init() {
        loadRequestCount()
    }
    
    // Charger le compteur de requêtes
    private func loadRequestCount() {
        requestCount = userDefaults.integer(forKey: requestCountKey)
    }
    
    // Incrémenter le compteur de requêtes
    func incrementRequestCount() {
        requestCount += 1
        userDefaults.set(requestCount, forKey: requestCountKey)
    }
    
    // Vérifier si l'utilisateur peut faire une requête
    func canMakeRequest(isSubscribed: Bool) -> Bool {
        if isSubscribed {
            return true
        }
        return requestCount < Self.freeRequestLimit
    }
    
    // Obtenir le nombre de requêtes restantes
    func remainingRequests(isSubscribed: Bool) -> Int {
        if isSubscribed {
            return -1 // Illimité
        }
        return max(0, Self.freeRequestLimit - requestCount)
    }
    
    // Réinitialiser le compteur (pour les tests)
    func resetCount() {
        requestCount = 0
        userDefaults.set(0, forKey: requestCountKey)
    }
    
    // Message pour l'utilisateur
    func getUsageMessage(isSubscribed: Bool) -> String {
        if isSubscribed {
            return "Abonnement actif - Requêtes illimitées"
        } else {
            let remaining = remainingRequests(isSubscribed: false)
            if remaining > 0 {
                return "\(remaining) requête\(remaining > 1 ? "s" : "") gratuite\(remaining > 1 ? "s" : "") restante\(remaining > 1 ? "s" : "")"
            } else {
                return "Requêtes gratuites épuisées"
            }
        }
    }
}

