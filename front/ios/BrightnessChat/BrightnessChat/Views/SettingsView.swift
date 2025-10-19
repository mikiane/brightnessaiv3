//
//  SettingsView.swift
//  BrightnessChat
//
//  Vue des paramètres et de gestion du compte
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var authManager: AuthenticationManager
    @EnvironmentObject var subscriptionManager: SubscriptionManager
    @EnvironmentObject var usageManager: UsageManager
    @Environment(\.dismiss) var dismiss
    @State private var showSubscriptionView = false
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.brightnessBackground
                    .ignoresSafeArea()
                
                List {
                    // Section Compte
                    Section {
                        HStack {
                            Image(systemName: "person.circle.fill")
                                .font(.title)
                                .foregroundColor(.brightnessAccent)
                            
                            VStack(alignment: .leading, spacing: 5) {
                                Text(authManager.userName ?? "Utilisateur")
                                    .font(.headline)
                                    .foregroundColor(.brightnessText)
                                
                                if let email = authManager.userEmail {
                                    Text(email)
                                        .font(.subheadline)
                                        .foregroundColor(.brightnessMuted)
                                }
                            }
                        }
                        .padding(.vertical, 5)
                    } header: {
                        Text("Compte")
                    }
                    
                    // Section Abonnement
                    Section {
                        if subscriptionManager.isSubscribed {
                            HStack {
                                Image(systemName: "crown.fill")
                                    .foregroundColor(.yellow)
                                
                                VStack(alignment: .leading, spacing: 5) {
                                    Text("Premium Actif")
                                        .font(.headline)
                                        .foregroundColor(.brightnessText)
                                    
                                    Text("Requêtes illimitées")
                                        .font(.subheadline)
                                        .foregroundColor(.brightnessMuted)
                                }
                                
                                Spacer()
                            }
                            .padding(.vertical, 5)
                            
                            Button(action: { openSubscriptionSettings() }) {
                                HStack {
                                    Text("Gérer l'abonnement")
                                        .foregroundColor(.brightnessAccent)
                                    Spacer()
                                    Image(systemName: "arrow.up.right.square")
                                        .foregroundColor(.brightnessAccent)
                                }
                            }
                        } else {
                            VStack(alignment: .leading, spacing: 10) {
                                HStack {
                                    Image(systemName: "bolt.fill")
                                        .foregroundColor(.brightnessAccent)
                                    
                                    VStack(alignment: .leading, spacing: 5) {
                                        Text("Gratuit")
                                            .font(.headline)
                                            .foregroundColor(.brightnessText)
                                        
                                        Text(usageManager.getUsageMessage(isSubscribed: false))
                                            .font(.subheadline)
                                            .foregroundColor(.brightnessMuted)
                                    }
                                    
                                    Spacer()
                                }
                                .padding(.vertical, 5)
                                
                                Button(action: { showSubscriptionView = true }) {
                                    HStack {
                                        Image(systemName: "crown.fill")
                                        Text("Passer à Premium")
                                        Spacer()
                                        Image(systemName: "chevron.right")
                                    }
                                    .foregroundColor(.white)
                                    .padding()
                                    .background(
                                        LinearGradient(
                                            colors: [.brightnessAccent, .blue],
                                            startPoint: .leading,
                                            endPoint: .trailing
                                        )
                                    )
                                    .cornerRadius(10)
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    } header: {
                        Text("Abonnement")
                    }
                    
                    // Section Actions
                    Section {
                        if !subscriptionManager.isSubscribed {
                            Button(action: {
                                Task {
                                    await subscriptionManager.restorePurchases()
                                }
                            }) {
                                HStack {
                                    Image(systemName: "arrow.clockwise")
                                    Text("Restaurer les achats")
                                    Spacer()
                                }
                                .foregroundColor(.brightnessAccent)
                            }
                        }
                        
                        #if DEBUG
                        Button(action: {
                            usageManager.resetCount()
                        }) {
                            HStack {
                                Image(systemName: "arrow.counterclockwise")
                                Text("Réinitialiser le compteur (Debug)")
                                Spacer()
                            }
                            .foregroundColor(.orange)
                        }
                        #endif
                        
                        Button(action: {
                            authManager.signOut()
                        }) {
                            HStack {
                                Image(systemName: "rectangle.portrait.and.arrow.right")
                                Text("Déconnexion")
                                Spacer()
                            }
                            .foregroundColor(.red)
                        }
                    }
                    
                    // Section À propos
                    Section {
                        HStack {
                            Text("Version")
                            Spacer()
                            Text("1.0.0")
                                .foregroundColor(.brightnessMuted)
                        }
                    } header: {
                        Text("À propos")
                    }
                }
                .listStyle(.insetGrouped)
                .scrollContentBackground(.hidden)
            }
            .navigationTitle("Paramètres")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Fermer") {
                        dismiss()
                    }
                    .foregroundColor(.brightnessAccent)
                }
            }
        }
        .sheet(isPresented: $showSubscriptionView) {
            SubscriptionView()
                .environmentObject(subscriptionManager)
                .environmentObject(usageManager)
        }
    }
    
    private func openSubscriptionSettings() {
        if let url = URL(string: "https://apps.apple.com/account/subscriptions") {
            UIApplication.shared.open(url)
        }
    }
}

#Preview {
    SettingsView()
        .environmentObject(AuthenticationManager())
        .environmentObject(SubscriptionManager())
        .environmentObject(UsageManager())
}

