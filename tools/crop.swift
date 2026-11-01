// 用法: swift crop.swift 源图 输出 x y 宽 高 [输出宽度] [质量0-1]
// 从源图裁出 (x, y, 宽, 高) 的区域，可按输出宽度等比缩放，存为 JPEG。
import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let a = CommandLine.arguments
guard a.count >= 7,
      let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: a[1]) as CFURL, nil),
      let full = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
    FileHandle.standardError.write("参数不对或读不了源图\n".data(using: .utf8)!); exit(1)
}
let rect = CGRect(x: Double(a[3])!, y: Double(a[4])!, width: Double(a[5])!, height: Double(a[6])!)
guard var img = full.cropping(to: rect) else { exit(2) }
if a.count >= 8, let outW = Int(a[7]), outW != img.width {
    let outH = Int((Double(img.height) * Double(outW) / Double(img.width)).rounded())
    let ctx = CGContext(data: nil, width: outW, height: outH, bitsPerComponent: 8, bytesPerRow: 0,
                        space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.interpolationQuality = .high
    ctx.draw(img, in: CGRect(x: 0, y: 0, width: outW, height: outH))
    img = ctx.makeImage()!
}
let q = a.count >= 9 ? Double(a[8])! : 0.8
let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: a[2]) as CFURL, UTType.jpeg.identifier as CFString, 1, nil)!
CGImageDestinationAddImage(dest, img, [kCGImageDestinationLossyCompressionQuality: q] as CFDictionary)
guard CGImageDestinationFinalize(dest) else { exit(3) }
print("\(a[2]) \(img.width)x\(img.height)")
