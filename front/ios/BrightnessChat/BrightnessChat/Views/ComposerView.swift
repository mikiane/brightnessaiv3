//
//  ComposerView.swift
//  BrightnessChat
//
//  Zone de saisie du message
//

import SwiftUI

struct ComposerView: View {
    @Binding var text: String
    let isSending: Bool
    let statusText: String
    let onSend: () -> Void
    let onStop: () -> Void
    
    var body: some View {
        VStack(spacing: 0) {
            Rectangle()
                .fill(Color.brightnessMuted)
                .frame(height: 1)
            
            VStack(spacing: 8) {
                HStack(spacing: 10) {
                    // TextField
                    TextField("Votre question… (Entrée = envoyer)", text: $text, axis: .vertical)
                        .lineLimit(3...6)
                        .padding(10)
                        .background(Color.brightnessPanel)
                        .foregroundColor(.brightnessText)
                        .cornerRadius(10)
                        .overlay(
                            RoundedRectangle(cornerRadius: 10)
                                .stroke(Color.brightnessMuted, lineWidth: 1)
                        )
                        .disabled(isSending)
                        .onSubmit {
                            if !text.isEmpty && !isSending {
                                onSend()
                            }
                        }
                    
                    // Bouton Stop (conditionnel)
                    if isSending {
                        Button(action: onStop) {
                            Text("Stop")
                                .font(.system(size: 14))
                                .foregroundColor(.brightnessText)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 10)
                                .background(Color.brightnessPanel)
                                .cornerRadius(10)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 10)
                                        .stroke(Color.brightnessMuted, lineWidth: 1)
                                )
                        }
                    }
                    
                    // Bouton Envoyer
                    Button(action: onSend) {
                        Text("Envoyer")
                            .font(.system(size: 14))
                            .foregroundColor(.white)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 10)
                            .background(
                                LinearGradient(
                                    colors: [Color.brightnessAccent, Color(hex: "b32f23")],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                            .cornerRadius(10)
                    }
                    .disabled(text.isEmpty || isSending)
                    .opacity(text.isEmpty || isSending ? 0.5 : 1)
                }
                
                // Statut
                if !statusText.isEmpty {
                    HStack {
                        Text(statusText)
                            .font(.system(size: 12))
                            .foregroundColor(.brightnessSubtle)
                        Spacer()
                    }
                }
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
            .background(Color.brightnessPanel)
        }
    }
}

