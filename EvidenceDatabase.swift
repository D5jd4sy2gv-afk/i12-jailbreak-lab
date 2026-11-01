import Foundation

struct EvidenceRecord: Identifiable {
    let id: String
    let title: String
    let status: String
    let confidence: String
    let detail: String
    let url: URL
}

struct EvidenceDatabase {
    static let snapshotDate = "2026-11-01"
    static let target = "iPhone13,2 · A14 · iOS 27.0 · 24A437"
    static let records: [EvidenceRecord] = [
        .init(id: "liter8-device-scope", title: "Liter8 设备范围", status: "仅 iPhone 11 已测试", confidence: "高", detail: "项目说明明确称其只对 iPhone 11（n104ap）作出支持声明；11 Pro / Pro Max 为实验性且未验证，不包含 iPhone 12 / A14。", url: URL(string: "https://github.com/Xplo8E/Liter8")!),
        .init(id: "liter8-build", title: "Build 24A437 记录", status: "其他设备的测试记录", confidence: "高", detail: "24A437 在 Liter8 表中对应 iPhone 11 的 run 记录，以及 11 Pro / Pro Max 的 experimental 记录，不能推导到 iPhone13,2。", url: URL(string: "https://github.com/Xplo8E/Liter8")!),
        .init(id: "iphone12-issue", title: "iPhone 12 支持讨论", status: "请求不等于支持确认", confidence: "高", detail: "近期 GitHub Issue 是关于 A14 支持的提问，不是维护者确认成功移植或可复现测试。", url: URL(string: "https://github.com/Xplo8E/Liter8/issues/29")!),
        .init(id: "a14-scope", title: "A14 / usbliter8", status: "未证实", confidence: "中", detail: "当前公开项目没有提供 iPhone 12 / A14 的可复现测试结果。A13 设备的结果不能作为 A14 证据。", url: URL(string: "https://github.com/Xplo8E/Liter8")!),
        .init(id: "firmware-signing", title: "iOS 27.0 签名状态", status: "第三方目录报告已停止签名", confidence: "中", detail: "第三方固件目录报告 24A437 已不再签名。不要为了研究而恢复或降级；实际签名状态应以 Apple 服务实时结果为准。", url: URL(string: "https://www.applefirmwares.com/firmware/iPhone13%2C2/27.0")!),
        .init(id: "current-firmware", title: "后续固件目录", status: "27.2 已列出", confidence: "中", detail: "Apple Wiki 固件索引列出 iPhone13,2 的 iOS 27.2 / 24B119。固件版本存在不代表有越狱支持。", url: URL(string: "https://theapplewiki.com/wiki/Firmware/iPhone/27.x")!)
    ]
}
