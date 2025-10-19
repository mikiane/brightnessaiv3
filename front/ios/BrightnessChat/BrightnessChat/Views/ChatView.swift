//
//  ChatView.swift
//  BrightnessChat
//
//  Vue principale du chat
//

import SwiftUI

struct ChatView: View {
    @StateObject private var viewModel = ChatViewModel()
    @State private var inputText = ""
    @FocusState private var isInputFocused: Bool
    
    var body: some View {
        ZStack {
            Color.brightnessBackground
                .ignoresSafeArea()
            
            if viewModel.isLoading {
                // Écran de chargement
                VStack(spacing: 20) {
                    ProgressView()
                        .scaleEffect(1.5)
                        .tint(.brightnessAccent)
                    
                    Text("Chargement...")
                        .foregroundColor(.brightnessText)
                        .font(.headline)
                }
            } else {
                VStack(spacing: 0) {
                    // Header
                    headerView
                    
                    // Messages
                    ScrollViewReader { proxy in
                        ScrollView {
                            LazyVStack(spacing: 10) {
                                ForEach(viewModel.messages) { message in
                                    MessageRow(message: message)
                                        .id(message.id)
                                }
                                
                                if viewModel.isSending {
                                    TypingIndicator()
                                        .padding(.leading, 46)
                                }
                            }
                            .padding(14)
                        }
                        .onChange(of: viewModel.messages.count) { _ in
                            if let lastMessage = viewModel.messages.last {
                                withAnimation {
                                    proxy.scrollTo(lastMessage.id, anchor: .bottom)
                                }
                            }
                        }
                    }
                    
                    Spacer()
                    
                    // Composer
                    ComposerView(
                        text: $inputText,
                        isSending: viewModel.isSending,
                        statusText: viewModel.statusText,
                        onSend: {
                            viewModel.sendMessage(inputText)
                            inputText = ""
                        },
                        onStop: {
                            viewModel.stopGeneration()
                        }
                    )
                    .focused($isInputFocused)
                }
            }
        }
        .alert("Erreur", isPresented: .constant(viewModel.errorMessage != nil)) {
            Button("OK") {
                viewModel.errorMessage = nil
            }
        } message: {
            if let error = viewModel.errorMessage {
                Text(error)
            }
        }
    }
    
    private var headerView: some View {
        HStack(spacing: 10) {
            if let config = viewModel.config, !config.logoUrl.isEmpty {
                // Charger l'image depuis le bundle ou URL
                if let bundleImage = UIImage(named: config.logoUrl.replacingOccurrences(of: "img/", with: "").replacingOccurrences(of: ".jpeg", with: "").replacingOccurrences(of: ".png", with: "")) {
                    Image(uiImage: bundleImage)
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: 28, height: 28)
                        .clipShape(RoundedRectangle(cornerRadius: 4))
                } else {
                    AsyncImage(url: URL(string: config.logoUrl)) { phase in
                        switch phase {
                        case .empty:
                            ProgressView()
                                .frame(width: 28, height: 28)
                        case .success(let image):
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                                .frame(width: 28, height: 28)
                                .clipShape(RoundedRectangle(cornerRadius: 4))
                        case .failure:
                            // Icône par défaut si échec
                            ZStack {
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(Color.brightnessAccent)
                                    .frame(width: 28, height: 28)
                                Text("BC")
                                    .font(.system(size: 10, weight: .bold))
                                    .foregroundColor(.white)
                            }
                        @unknown default:
                            EmptyView()
                        }
                    }
                }
            }
            
            Text(viewModel.config?.title ?? "Chat RAG")
                .font(.headline)
                .foregroundColor(.brightnessText)
            
            Spacer()
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
        .background(Color.brightnessPanel)
        .overlay(
            Rectangle()
                .frame(height: 1)
                .foregroundColor(.brightnessMuted),
            alignment: .bottom
        )
    }
}

#Preview {
    ChatView()
}

