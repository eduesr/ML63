import Foundation
import Quartz
import Vision

func ocrPDF(path: String) {
    let url = URL(fileURLWithPath: path)
    guard let document = PDFDocument(url: url) else {
        print("Could not open PDF: \(path)")
        return
    }
    
    print("Total pages: \(document.pageCount)")
    
    for i in 0..<document.pageCount {
        guard let page = document.page(at: i) else { continue }
        // Create an image representation of the PDF page
        let pageRect = page.bounds(for: .mediaBox)
        let renderer = NSImage(size: pageRect.size)
        renderer.lockFocus()
        if let context = NSGraphicsContext.current?.cgContext {
            context.setFillColor(NSColor.white.cgColor)
            context.fill(CGRect(origin: .zero, size: pageRect.size))
            page.draw(with: .mediaBox, to: context)
        }
        renderer.unlockFocus()
        
        guard let cgImage = renderer.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
            print("Could not convert page \(i+1) to CGImage")
            continue
        }
        
        let requestHandler = VNImageRequestHandler(cgImage: cgImage, options: [:])
        let request = VNRecognizeTextRequest { request, error in
            if let error = error {
                print("Error: \(error)")
                return
            }
            guard let observations = request.results as? [VNRecognizedTextObservation] else { return }
            print("=== PAGE \(i+1) OCR RESULTS ===")
            for observation in observations {
                guard let topCandidate = observation.topCandidates(1).first else { continue }
                print(topCandidate.string)
            }
        }
        request.recognitionLevel = .accurate
        request.usesLanguageCorrection = true
        request.recognitionLanguages = ["es"]
        
        do {
            try requestHandler.perform([request])
        } catch {
            print("Failed to perform OCR request: \(error)")
        }
    }
}

let args = CommandLine.arguments
if args.count < 2 {
    print("Usage: ocr <pdf-file-path>")
} else {
    ocrPDF(path: args[1])
}
