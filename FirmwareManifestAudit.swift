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
        guard let dictionary = plist as? [String: Any] else { throw ManifestError.invalidFormat }
        let version = dictionary["ProductVersion"] as? String ?? "未知"
        let build = dictionary["ProductBuildVersion"] as? String ?? "未知"
        let products = dictionary["SupportedProductTypes"] as? [String] ?? []
        guard version != "未知" || build != "未知" || !products.isEmpty else { throw ManifestError.missingFields }
        return FirmwareManifestAudit(productVersion: version, buildVersion: build,
                                     supportedProductTypes: products.sorted(),
                                     matchesTargetModel: products.contains(targetProductType),
                                     matchesTargetBuild: build == targetBuild)
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
        case .invalidFormat: return "文件不是有效的 Property List。请选取 BuildManifest.plist。"
        case .missingFields: return "清单缺少 ProductVersion、ProductBuildVersion 和 SupportedProductTypes 等关键字段。"
        }
    }
}

// Online catalogue metadata only. This endpoint does not download the IPSW or BuildManifest.plist.
struct FirmwareCatalogResponse: Decodable {
    let identifier: String
    let firmwares: [FirmwareCatalogEntry]
}

struct FirmwareCatalogEntry: Decodable, Identifiable {
    let identifier: String?
    let version: String
    let buildid: String
    let signed: Bool?
    let filesize: Int64?
    let releasedate: String?
    let url: String?

    var id: String { "\(buildid)-\(version)" }
    var sizeLabel: String {
        guard let filesize, filesize > 0 else { return "大小未知" }
        let gib = Double(filesize) / 1_073_741_824
        return String(format: "%.2f GiB", gib)
    }
    var signingLabel: String {
        guard let signed else { return "签名状态未知" }
        return signed ? "Apple 当前签名" : "Apple 已停止签名"
    }
}

enum FirmwareCatalogService {
    static func fetch(for productType: String = "iPhone13,2") async throws -> [FirmwareCatalogEntry] {
        guard let url = URL(string: "https://api.ipsw.me/v4/device/\(productType)?type=ipsw") else {
            throw FirmwareCatalogError.invalidURL
        }
        var request = URLRequest(url: url)
        request.timeoutInterval = 20
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
            throw FirmwareCatalogError.serverResponse
        }
        let decoded = try JSONDecoder().decode(FirmwareCatalogResponse.self, from: data)
        guard decoded.identifier == productType else { throw FirmwareCatalogError.deviceMismatch }
        return decoded.firmwares.sorted { lhs, rhs in
            if lhs.releasedate != rhs.releasedate { return (lhs.releasedate ?? "") > (rhs.releasedate ?? "") }
            return lhs.version > rhs.version
        }
    }
}

enum FirmwareCatalogError: LocalizedError {
    case invalidURL, serverResponse, deviceMismatch
    var errorDescription: String? {
        switch self {
        case .invalidURL: return "固件查询地址无效。"
        case .serverResponse: return "固件目录暂时无法访问，请稍后重试。"
        case .deviceMismatch: return "服务器返回的设备标识不匹配，已停止显示结果。"
        }
    }
}
