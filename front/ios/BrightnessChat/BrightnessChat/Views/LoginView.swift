//
//  LoginView.swift
//  BrightnessChat
//
//  Vue de connexion avec Sign in with Apple
//

import SwiftUI
import AuthenticationServices

struct LoginView: View {
    @EnvironmentObject var authManager: AuthenticationManager
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    var body: some View {
        ZStack {
            Color.brightnessBackground
                .ignoresSafeArea()
            
            VStack(spacing: 30) {
                // Logo et titre
                VStack(spacing: 15) {
                    if let logoImage = UIImage(named: "logo-brightness") {
                        Image(uiImage: logoImage)
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(width: 120, height: 120)
                            .clipShape(RoundedRectangle(cornerRadius: 20))
                            .shadow(color: .black.opacity(0.2), radius: 10, x: 0, y: 5)
                    }
                    
                    Text("Brightness Chat")
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.brightnessText)
                    
                    Text("Connectez-vous pour commencer")
                        .font(.subheadline)
                        .foregroundColor(.brightnessMuted)
                }
                .padding(.top, 60)
                
                Spacer()
                
                // Informations sur l'offre
                VStack(spacing: 20) {
                    FeatureRow(icon: "checkmark.circle.fill", text: "5 requêtes gratuites")
                    FeatureRow(icon: "crown.fill", text: "Requêtes illimitées avec l'abonnement")
                    FeatureRow(icon: "lock.shield.fill", text: "Vos données sont sécurisées")
                }
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 15)
                        .fill(Color.brightnessPanel)
                )
                .padding(.horizontal)
                
                Spacer()
                
                // Bouton Sign in with Apple
                VStack(spacing: 15) {
                    if isLoading {
                        ProgressView()
                            .scaleEffect(1.2)
                            .tint(.white)
                            .frame(height: 50)
                    } else {
                        SignInWithAppleButton(
                            .signIn,
                            onRequest: { request in
                                request.requestedScopes = [.fullName, .email]
                            },
                            onCompletion: { result in
                                handleSignIn(result: result)
                            }
                        )
                        .signInWithAppleButtonStyle(.black)
                        .frame(height: 50)
                        .cornerRadius(8)
                    }
                    
                    if let error = errorMessage {
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.red)
                            .multilineTextAlignment(.center)
                    }
                    
                    Text("En vous connectant, vous acceptez nos conditions d'utilisation")
                        .font(.caption)
                        .foregroundColor(.brightnessMuted)
                        .multilineTextAlignment(.center)
                }
                .padding(.horizontal, 30)
                .padding(.bottom, 40)
            }
        }
    }
    
    private func handleSignIn(result: Result<ASAuthorization, Error>) {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                switch result {
                case .success(let authorization):
                    if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
                        authManager.handleSignInSuccess(
                            userID: appleIDCredential.user,
                            email: appleIDCredential.email,
                            fullName: appleIDCredential.fullName
                        )
                    }
                case .failure(let error):
                    errorMessage = "Erreur de connexion: \(error.localizedDescription)"
                }
                isLoading = false
            }
        }
    }
}

struct FeatureRow: View {
    let icon: String
    let text: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(.brightnessAccent)
                .frame(width: 30)
            
            Text(text)
                .font(.body)
                .foregroundColor(.brightnessText)
            
            Spacer()
        }
    }
}

#Preview {
    LoginView()
        .environmentObject(AuthenticationManager())
}

