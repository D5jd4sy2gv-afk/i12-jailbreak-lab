import Foundation

struct FirmwareManifestAudit {
    let productVersion: String
    let buildVersion: String
    let supportedProductTypes: [String]
    let matchesTargetModel: Bool
    let matchesTargetBuild: Bool

    static func inspect(url: URL, targetProductType: String = "iPhone13,2", targetBuild: String = "24A437") throws -> FirmwareManifestAudit {
        let hasAccess = url.startAccessingSecurityScopedResource()
        defer { if hasAccess { url.stopAccessingSecurityScopedResource() } }
        let data = try Data(contentsOf: url)
        let plist = try PropertyListSerialization.propertyList(from: data, options: [], format: nil)
        guard let dictionary = plist as? [String: Any] else {
            throw ManifestError.invalidFormat
        }
        let version = dictionary["ProductVersion"] as? String ?? "未知"
        let build = dictionary["ProductBuildVersion"] as? String ?? "未知"
        let products = dictionary["SupportedProductTypes"] as? [String] ?? []
        guard version != "未知" || build != "未知" || !products.isEmpty else {
            throw ManifestError.missingFields
        }
        return FirmwareManifestAudit(
            productVersion: version,
            buildVersion: build,
            supportedProductTypes: products.sorted(),
            matchesTargetModel: products.contains(targetProductType),
            matchesTargetBuild: build == targetBuild
        )
    }

    var summary: String {
        """
        固件清单检查结果
        ProductVersion：\(productVersion)
        ProductBuildVersion：\(buildVersion)
        包含目标设备 iPhone13,2：\(matchesTargetModel ? "是" : "否")
        匹配目标 Build 24A437：\(matchesTargetBuild ? "是" : "否")
        SupportedProductTypes：\(supportedProductTypes.joined(separator: ", "))

        注意：清单匹配只证明固件元数据对应，不证明漏洞、提权或越狱兼容性。
        """
    }
}

enum ManifestError: LocalizedError {
    case invalidFormat
    case missingFields

    var errorDescription: String? {
        switch self {
        case .invalidFormat: return "文件不是有效的 Property List。请选取从 IPSW 中提取的 BuildManifest.plist。"
        case .missingFields: return "清单缺少 ProductVersion、ProductBuildVersion 和 SupportedProductTypes 等关键字段。"
        }
    }
}
