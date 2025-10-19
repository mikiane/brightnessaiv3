//
//  SubscriptionManager.swift
//  BrightnessChat
//
//  Gestion des abonnements avec StoreKit 2
//

import Foundation
import StoreKit

@MainActor
class SubscriptionManager: ObservableObject {
    @Published var isSubscribed = false
    @Published var subscriptionProduct: Product?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    // ID du produit d'abonnement (à configurer dans App Store Connect)
    private let subscriptionProductID = "com.brightness.chat.monthly"
    
    private var updateListenerTask: Task<Void, Error>?
    
    init() {
        updateListenerTask = listenForTransactions()
        
        Task {
            await loadProducts()
            await updateSubscriptionStatus()
        }
    }
    
    deinit {
        updateListenerTask?.cancel()
    }
    
    // Charger les produits depuis l'App Store
    func loadProducts() async {
        do {
            let products = try await Product.products(for: [subscriptionProductID])
            subscriptionProduct = products.first
        } catch {
            errorMessage = "Impossible de charger les produits: \(error.localizedDescription)"
        }
    }
    
    // Acheter l'abonnement
    func purchase() async {
        guard let product = subscriptionProduct else {
            errorMessage = "Produit non disponible"
            return
        }
        
        isLoading = true
        
        do {
            let result = try await product.purchase()
            
            switch result {
            case .success(let verification):
                // Vérifier la transaction
                let transaction = try checkVerified(verification)
                
                // Mettre à jour le statut d'abonnement
                await updateSubscriptionStatus()
                
                // Finaliser la transaction
                await transaction.finish()
                
                isLoading = false
                
            case .userCancelled:
                isLoading = false
                
            case .pending:
                isLoading = false
                errorMessage = "Achat en attente"
                
            @unknown default:
                isLoading = false
            }
        } catch {
            isLoading = false
            errorMessage = "Erreur d'achat: \(error.localizedDescription)"
        }
    }
    
    // Restaurer les achats
    func restorePurchases() async {
        isLoading = true
        
        do {
            try await AppStore.sync()
            await updateSubscriptionStatus()
            isLoading = false
        } catch {
            isLoading = false
            errorMessage = "Erreur de restauration: \(error.localizedDescription)"
        }
    }
    
    // Mettre à jour le statut d'abonnement
    func updateSubscriptionStatus() async {
        var activeSubscriptions: [Product] = []
        
        // Vérifier tous les abonnements actifs
        for await result in Transaction.currentEntitlements {
            do {
                let transaction = try checkVerified(result)
                
                // Vérifier si l'abonnement est toujours actif
                if let product = subscriptionProduct,
                   transaction.productID == product.id {
                    activeSubscriptions.append(product)
                }
            } catch {
                print("Transaction verification failed: \(error)")
            }
        }
        
        isSubscribed = !activeSubscriptions.isEmpty
    }
    
    // Écouter les mises à jour de transactions
    private func listenForTransactions() -> Task<Void, Error> {
        return Task.detached {
            for await result in Transaction.updates {
                do {
                    let transaction = try self.checkVerified(result)
                    
                    await self.updateSubscriptionStatus()
                    
                    await transaction.finish()
                } catch {
                    print("Transaction failed verification: \(error)")
                }
            }
        }
    }
    
    // Vérifier qu'une transaction est valide
    private func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified:
            throw StoreError.failedVerification
        case .verified(let safe):
            return safe
        }
    }
    
    // Obtenir le prix formaté
    var formattedPrice: String {
        subscriptionProduct?.displayPrice ?? "15,00 €"
    }
}

enum StoreError: Error {
    case failedVerification
}

