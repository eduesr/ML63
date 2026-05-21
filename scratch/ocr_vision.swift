import Foundation
import PDFKit
import Vision

// Ensure we have a file path argument
guard CommandLine.arguments.count > 1 else {
    print("Usage: swift ocr_vision.swift <path-to-pdf>")
    exit(1)
}

let pdfPath = CommandLine.arguments[1]
let url = URL(fileURLWithPath: pdfPath)

guard let document = PDFDocument(url: url) else {
    print("Error: Could not open PDF file at \(pdfPath)")
    exit(1)
}

print("Successfully loaded PDF with \(document.pageCount) pages.")

for i in 0..<document.pageCount {
    guard let page = document.page(at: i) else {
        print("Could not load page \(i + 1)")
        continue
    }
    
    // Render the PDF page to a CGImage at 2x resolution for OCR accuracy
    let pageRect = page.bounds(for: .mediaBox)
    let scale: CGFloat = 2.0
    let width = Int(pageRect.width * scale)
    let height = Int(pageRect.height * scale)
    
    let colorSpace = CGColorSpaceCreateDeviceRGB()
    guard let context = CGContext(
        data: nil,
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: 0,
        space: colorSpace,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
    ) else {
        print("Failed to create CGContext for page \(i + 1)")
        continue
    }
    
    // Fill background with white
    context.setFillColor(red: 1.0, green: 1.0, blue: 1.0, alpha: 1.0)
    context.fill(CGRect(x: 0, y: 0, width: width, height: height))
    
    // Draw PDF page into context at 2x scale
    context.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: context)
    
    guard let cgImage = context.makeImage() else {
        print("Failed to render image for page \(i + 1)")
        continue
    }
    
    // Perform OCR using Apple Vision
    let requestHandler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    
    var pageText = ""
    let request = VNRecognizeTextRequest { (request, error) in
        if let error = error {
            print("Vision error: \(error)")
            return
        }
        guard let observations = request.results as? [VNRecognizedTextObservation] else { return }
        let recognizedStrings = observations.compactMap { observation in
            observation.topCandidates(1).first?.string
        }
        pageText = recognizedStrings.joined(separator: "\n")
    }
    
    // Configure for Spanish language
    request.recognitionLanguages = ["es-ES"]
    request.usesLanguageCorrection = true
    
    do {
        try requestHandler.perform([request])
        print("\n--- PAGE \(i + 1) ---")
        print(pageText)
    } catch {
        print("OCR execution error on page \(i + 1): \(error)")
    }
}
