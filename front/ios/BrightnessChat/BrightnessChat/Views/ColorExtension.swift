//
//  ColorExtension.swift
//  BrightnessChat
//
//  Extensions de couleurs pour le design system
//

import SwiftUI

extension Color {
    // Design System Brightness
    static let brightnessBackground = Color(hex: "0B0B0C")
    static let brightnessPanel = Color(hex: "15161A")
    static let brightnessMuted = Color(hex: "24262B")
    static let brightnessText = Color(hex: "E8E9EC")
    static let brightnessAccent = Color(hex: "D73C2C")
    static let brightnessSubtle = Color(hex: "9AA0A6")
    
    // Initialisation depuis hex
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

