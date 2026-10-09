// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "h2o2-apple-translate",
    platforms: [.macOS("26.0")],
    products: [.executable(name: "h2o2-apple-translate", targets: ["AppleTranslate"])],
    targets: [.executableTarget(name: "AppleTranslate", path: "Sources/AppleTranslate")]
)
