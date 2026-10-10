import Foundation
import Translation

// Input: {"requests": [{"id": "...", "text": "..."}]}
// Output: {"translations": [{"id": "...", "text": "..."}]}
// This tool requires macOS 26+ and locally installed English/Chinese translation resources.

struct InputRequest: Decodable, Sendable {
    let id: String
    let text: String
}
struct InputEnvelope: Decodable, Sendable {
    let requests: [InputRequest]
}
struct OutputTranslation: Encodable, Sendable {
    let id: String
    let text: String
}
struct OutputEnvelope: Encodable, Sendable {
    let translations: [OutputTranslation]
}

@main
struct AppleTranslate {
    // Keep non-Sendable framework requests off the main actor.
    nonisolated static func translate(_ envelope: InputEnvelope) async throws -> OutputEnvelope {
        // Direct initialization without a SwiftUI view is supported in macOS 26+.
        // It does not trigger language downloads; install the language pair first.
        let session = TranslationSession(
            installedSource: Locale.Language(identifier: "en"),
            target: Locale.Language(identifier: "zh-Hans")
        )
        let requests = envelope.requests.map {
            TranslationSession.Request(sourceText: $0.text, clientIdentifier: $0.id)
        }
        let translated = try await session.translations(from: requests)
        // translations(from:) documents result order matching request order.
        guard translated.count == envelope.requests.count else {
            throw NSError(domain: "H2O2Translation", code: 2,
                          userInfo: [NSLocalizedDescriptionKey: "Translation count mismatch"])
        }
        let result = zip(envelope.requests, translated).map { item, response in
            OutputTranslation(id: item.id, text: response.targetText)
        }
        return OutputEnvelope(translations: result)
    }

    @MainActor
    static func main() async {
        do {
            let bytes = FileHandle.standardInput.readDataToEndOfFile()
            let envelope = try JSONDecoder().decode(InputEnvelope.self, from: bytes)
            if envelope.requests.isEmpty {
                FileHandle.standardOutput.write(try JSONEncoder().encode(OutputEnvelope(translations: [])))
                return
            }
            let output = try await translate(envelope)
            FileHandle.standardOutput.write(try JSONEncoder().encode(output))
        } catch {
            let reason = "Apple Translation failed: \(error)\n" +
              "Check macOS 26+ and install English / Simplified Chinese in System Settings > Language & Region > Translation Languages.\n"
            FileHandle.standardError.write(Data(reason.utf8))
            Foundation.exit(2)
        }
    }
}
