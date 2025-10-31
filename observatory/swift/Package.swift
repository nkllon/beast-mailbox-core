// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required

import PackageDescription

let package = Package(
    name: "ObservatoryApp",
    platforms: [
        .macOS(.v13) // macOS 13.0+ (Command Line Tools compatibility)
        // Note: For macOS 15.0+ features (Apple Intelligence), use latest Xcode
    ],
    products: [
        .executable(
            name: "ObservatoryApp",
            targets: ["ObservatoryApp"]
        ),
    ],
    dependencies: [
        // No external dependencies needed - using built-in frameworks
    ],
    targets: [
        .executableTarget(
            name: "ObservatoryApp",
            dependencies: [],
            path: "Sources"
        ),
        .testTarget(
            name: "ObservatoryAppTests",
            dependencies: ["ObservatoryApp"],
            path: "Tests/ObservatoryAppTests"
        ),
    ]
)

