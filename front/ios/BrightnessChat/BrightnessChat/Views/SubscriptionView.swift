//
//  SubscriptionView.swift
//  BrightnessChat
//
//  Vue pour gérer l'abonnement
//

import SwiftUI

struct SubscriptionView: View {
    @EnvironmentObject var subscriptionManager: SubscriptionManager
    @EnvironmentObject var usageManager: UsageManager
    @Environment(\.dismiss) var dismiss
    
    var showDismissButton: Bool = true
    
    var body: some View {
        ZStack {
            Color.brightnessBackground
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 30) {
                    // Header
                    VStack(spacing: 10) {
                        Image(systemName: "crown.fill")
                            .font(.system(size: 60))
                            .foregroundColor(.yellow)
                            .padding(.top, 40)
                        
                        Text("Passez à Premium")
                            .font(.system(size: 32, weight: .bold))
                            .foregroundColor(.brightnessText)
                        
                        Text("Requêtes illimitées avec l'IA")
                            .font(.headline)
                            .foregroundColor(.brightnessMuted)
                    }
                    
                    // Statut actuel
                    VStack(spacing: 12) {
                        if subscriptionManager.isSubscribed {
                            HStack {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.green)
                                Text("Abonnement actif")
                                    .font(.headline)
                                    .foregroundColor(.brightnessText)
                            }
                            .padding()
                            .frame(maxWidth: .infinity)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color.green.opacity(0.2))
                            )
                        } else {
                            VStack(spacing: 8) {
                                Text(usageManager.getUsageMessage(isSubscribed: false))
                                    .font(.headline)
                                    .foregroundColor(.brightnessText)
                                
                                if usageManager.requestCount >= UsageManager.freeRequestLimit {
                                    Text("Abonnez-vous pour continuer")
                                        .font(.subheadline)
                                        .foregroundColor(.red)
                                }
                            }
                            .padding()
                            .frame(maxWidth: .infinity)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color.brightnessPanel)
                            )
                        }
                    }
                    .padding(.horizontal)
                    
                    // Fonctionnalités Premium
                    VStack(alignment: .leading, spacing: 20) {
                        Text("Avec l'abonnement Premium :")
                            .font(.headline)
                            .foregroundColor(.brightnessText)
                        
                        PremiumFeature(icon: "infinity", title: "Requêtes illimitées", description: "Posez autant de questions que vous voulez")
                        PremiumFeature(icon: "bolt.fill", title: "Réponses prioritaires", description: "Bénéficiez de la meilleure performance")
                        PremiumFeature(icon: "sparkles", title: "Accès à toutes les fonctionnalités", description: "Profitez de toutes les capacités de l'IA")
                        PremiumFeature(icon: "arrow.clockwise", title: "Annulation facile", description: "Résiliez à tout moment")
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 15)
                            .fill(Color.brightnessPanel)
                    )
                    .padding(.horizontal)
                    
                    // Prix et bouton d'abonnement
                    if !subscriptionManager.isSubscribed {
                        VStack(spacing: 20) {
                            VStack(spacing: 5) {
                                Text(subscriptionManager.formattedPrice)
                                    .font(.system(size: 48, weight: .bold))
                                    .foregroundColor(.brightnessText)
                                
                                Text("par mois")
                                    .font(.subheadline)
                                    .foregroundColor(.brightnessMuted)
                            }
                            
                            if subscriptionManager.isLoading {
                                ProgressView()
                                    .scaleEffect(1.2)
                                    .tint(.white)
                                    .frame(height: 50)
                            } else {
                                Button(action: {
                                    Task {
                                        await subscriptionManager.purchase()
                                    }
                                }) {
                                    Text("S'abonner maintenant")
                                        .font(.headline)
                                        .foregroundColor(.white)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 50)
                                        .background(
                                            LinearGradient(
                                                colors: [.brightnessAccent, .blue],
                                                startPoint: .leading,
                                                endPoint: .trailing
                                            )
                                        )
                                        .cornerRadius(12)
                                }
                                
                                Button(action: {
                                    Task {
                                        await subscriptionManager.restorePurchases()
                                    }
                                }) {
                                    Text("Restaurer les achats")
                                        .font(.subheadline)
                                        .foregroundColor(.brightnessAccent)
                                }
                            }
                            
                            if let error = subscriptionManager.errorMessage {
                                Text(error)
                                    .font(.caption)
                                    .foregroundColor(.red)
                                    .multilineTextAlignment(.center)
                            }
                        }
                        .padding()
                    }
                    
                    // Informations légales
                    VStack(spacing: 5) {
                        Text("Abonnement mensuel renouvelé automatiquement")
                            .font(.caption)
                            .foregroundColor(.brightnessMuted)
                        
                        Text("Annulation possible à tout moment dans les réglages de l'App Store")
                            .font(.caption)
                            .foregroundColor(.brightnessMuted)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.horizontal)
                    .padding(.bottom, 30)
                }
            }
        }
        .overlay(alignment: .topTrailing) {
            if showDismissButton {
                Button(action: { dismiss() }) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.title)
                        .foregroundColor(.brightnessMuted)
                        .padding()
                }
            }
        }
    }
}

struct PremiumFeature: View {
    let icon: String
    let title: String
    let description: String
    
    var body: some View {
        HStack(alignment: .top, spacing: 15) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.brightnessAccent)
                .frame(width: 30)
            
            VStack(alignment: .leading, spacing: 5) {
                Text(title)
                    .font(.headline)
                    .foregroundColor(.brightnessText)
                
                Text(description)
                    .font(.subheadline)
                    .foregroundColor(.brightnessMuted)
            }
        }
    }
}

#Preview {
    SubscriptionView()
        .environmentObject(SubscriptionManager())
        .environmentObject(UsageManager())
}

