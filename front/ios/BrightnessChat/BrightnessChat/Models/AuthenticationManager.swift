//
//  AuthenticationManager.swift
//  BrightnessChat
//
//  Gestion de l'authentification avec Sign in with Apple
//

import Foundation
import AuthenticationServices
import SwiftUI

@MainActor
class AuthenticationManager: NSObject, ObservableObject {
    @Published var isAuthenticated = false
    @Published var userID: String?
    @Published var userEmail: String?
    @Published var userName: String?
    
    private let userDefaults = UserDefaults.standard
    private let userIDKey = "brightness_user_id"
    private let userEmailKey = "brightness_user_email"
    private let userNameKey = "brightness_user_name"
    
    override init() {
        super.init()
        checkAuthenticationState()
    }
    
    func checkAuthenticationState() {
        if let savedUserID = userDefaults.string(forKey: userIDKey) {
            self.userID = savedUserID
            self.userEmail = userDefaults.string(forKey: userEmailKey)
            self.userName = userDefaults.string(forKey: userNameKey)
            self.isAuthenticated = true
        }
    }
    
    func signInWithApple() async throws {
        let appleIDProvider = ASAuthorizationAppleIDProvider()
        let request = appleIDProvider.createRequest()
        request.requestedScopes = [.fullName, .email]
        
        let authorizationController = ASAuthorizationController(authorizationRequests: [request])
        
        return try await withCheckedThrowingContinuation { continuation in
            let delegate = SignInDelegate(continuation: continuation, manager: self)
            authorizationController.delegate = delegate
            authorizationController.presentationContextProvider = delegate
            authorizationController.performRequests()
            
            // Garder une référence forte au delegate
            objc_setAssociatedObject(authorizationController, "delegate", delegate, .OBJC_ASSOCIATION_RETAIN)
        }
    }
    
    func handleSignInSuccess(userID: String, email: String?, fullName: PersonNameComponents?) {
        self.userID = userID
        self.userEmail = email
        
        if let fullName = fullName {
            let name = [fullName.givenName, fullName.familyName]
                .compactMap { $0 }
                .joined(separator: " ")
            self.userName = name.isEmpty ? nil : name
        }
        
        // Sauvegarder dans UserDefaults
        userDefaults.set(userID, forKey: userIDKey)
        if let email = email {
            userDefaults.set(email, forKey: userEmailKey)
        }
        if let userName = userName {
            userDefaults.set(userName, forKey: userNameKey)
        }
        
        self.isAuthenticated = true
    }
    
    func signOut() {
        userDefaults.removeObject(forKey: userIDKey)
        userDefaults.removeObject(forKey: userEmailKey)
        userDefaults.removeObject(forKey: userNameKey)
        
        self.userID = nil
        self.userEmail = nil
        self.userName = nil
        self.isAuthenticated = false
    }
}

// Delegate pour gérer les callbacks Sign in with Apple
class SignInDelegate: NSObject, ASAuthorizationControllerDelegate, ASAuthorizationControllerPresentationContextProviding {
    let continuation: CheckedContinuation<Void, Error>
    let manager: AuthenticationManager
    
    init(continuation: CheckedContinuation<Void, Error>, manager: AuthenticationManager) {
        self.continuation = continuation
        self.manager = manager
    }
    
    func authorizationController(controller: ASAuthorizationController, didCompleteWithAuthorization authorization: ASAuthorization) {
        if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
            let userID = appleIDCredential.user
            let email = appleIDCredential.email
            let fullName = appleIDCredential.fullName
            
            Task { @MainActor in
                manager.handleSignInSuccess(userID: userID, email: email, fullName: fullName)
                continuation.resume()
            }
        }
    }
    
    func authorizationController(controller: ASAuthorizationController, didCompleteWithError error: Error) {
        continuation.resume(throwing: error)
    }
    
    func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
        guard let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
              let window = windowScene.windows.first else {
            fatalError("No window found")
        }
        return window
    }
}

