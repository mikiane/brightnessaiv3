//
//  MessageRow.swift
//  BrightnessChat
//
//  Ligne de message dans le chat
//

import SwiftUI
import MarkdownUI

struct MessageRow: View {
    let message: Message
    
    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            // Avatar
            ZStack {
                Circle()
                    .fill(message.role == .assistant ? Color.brightnessAccent : Color.gray.opacity(0.3))
                    .frame(width: 36, height: 36)
                
                Text(message.role == .assistant ? "AI" : "Vous")
                    .font(.system(size: 10, weight: .bold))
                    .foregroundColor(.white)
            }
            
            // Contenu
            VStack(alignment: .leading, spacing: 4) {
                if message.role == .assistant {
                    Markdown(message.content)
                        .markdownTheme(.brightness)
                        .textSelection(.enabled)
                } else {
                    Text(message.content)
                        .foregroundColor(.brightnessText)
                        .textSelection(.enabled)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            
            Spacer()
        }
    }
}

// Extension pour le thème Markdown personnalisé
extension Theme {
    static let brightness = Theme()
        .text {
            ForegroundColor(.brightnessText)
            FontSize(16)
        }
        .code {
            FontFamilyVariant(.monospaced)
            BackgroundColor(Color(hex: "0f1115"))
            ForegroundColor(.brightnessText)
        }
        .link {
            ForegroundColor(.brightnessAccent)
        }
}

