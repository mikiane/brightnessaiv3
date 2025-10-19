//
//  TypingIndicator.swift
//  BrightnessChat
//
//  Indicateur de frappe (3 points animés)
//

import SwiftUI

struct TypingIndicator: View {
    @State private var animationStates = [false, false, false]
    
    var body: some View {
        HStack(spacing: 4) {
            ForEach(0..<3) { index in
                Circle()
                    .fill(Color.brightnessSubtle)
                    .frame(width: 6, height: 6)
                    .opacity(animationStates[index] ? 1.0 : 0.2)
                    .animation(
                        Animation.easeInOut(duration: 0.6)
                            .repeatForever()
                            .delay(Double(index) * 0.2),
                        value: animationStates[index]
                    )
            }
        }
        .onAppear {
            for index in 0..<3 {
                animationStates[index] = true
            }
        }
    }
}

#Preview {
    ZStack {
        Color.brightnessBackground
        TypingIndicator()
    }
}

