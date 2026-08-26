import Foundation
import Vision
import AppKit

let photosDir = "/Users/yangyongzhu/.gemini/antigravity/scratch/yang-pwa/photos"
let fileManager = FileManager.default

guard let files = try? fileManager.contentsOfDirectory(atPath: photosDir) else {
    print("Cannot open dir")
    exit(1)
}

let imageFiles = files.filter { $0.hasSuffix(".jpg") || $0.hasSuffix(".JPG") || $0.hasSuffix(".png") || $0.hasSuffix(".PNG") }.sorted()

for file in imageFiles {
    let fullPath = (photosDir as NSString).appendingPathComponent(file)
    guard let image = NSImage(contentsOfFile: fullPath),
          let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        continue
    }
    
    let requestHandler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    let request = VNRecognizeTextRequest()
    request.recognitionLanguages = ["ja-JP", "zh-Hant", "zh-Hans", "en-US"]
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    
    try? requestHandler.perform([request])
    
    guard let observations = request.results else { continue }
    let recognizedStrings = observations.compactMap { $0.topCandidates(1).first?.string }
    if !recognizedStrings.isEmpty {
        print("=== FILE: \(file) ===")
        for s in recognizedStrings {
            print("  \(s)")
        }
    }
}
