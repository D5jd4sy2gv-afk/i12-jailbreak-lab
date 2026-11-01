import Foundation
import UIKit
import Darwin

struct DeviceAudit {
    let machine: String
    let deviceName: String
    let chip: String
    let systemVersion: String
    let buildVersion: String
    let isTargetModel: Bool
    let isTargetBuild: Bool

    static func collect() -> DeviceAudit {
        var system = utsname()
        uname(&system)
        let machine = withUnsafePointer(to: &system.machine) {
            $0.withMemoryRebound(to: CChar.self, capacity: MemoryLayout.size(ofValue: system.machine)) {
                String(cString: $0)
            }
        }

        var build = [CChar](repeating: 0, count: 128)
        var size = build.count
        let result = sysctlbyname("kern.osversion", &build, &size, nil, 0)
        let buildString = result == 0 ? String(cString: build) : "读取不可用"
        let version = UIDevice.current.systemVersion
        let model = Self.models[machine]

        return DeviceAudit(
            machine: machine,
            deviceName: model?.name ?? "未识别设备",
            chip: model?.chip ?? "未知芯片",
            systemVersion: version,
            buildVersion: buildString,
            isTargetModel: machine == "iPhone13,2",
            isTargetBuild: version == "27.0" && buildString == "24A437"
        )
    }

    private static let models: [String: (name: String, chip: String)] = [
        "iPhone13,1": ("iPhone 12 mini", "A14 Bionic"),
        "iPhone13,2": ("iPhone 12", "A14 Bionic"),
        "iPhone13,3": ("iPhone 12 Pro", "A14 Bionic"),
        "iPhone13,4": ("iPhone 12 Pro Max", "A14 Bionic")
    ]

    var reportText: String {
        """
        i12 Jailbreak Lab V1.0 — 只读设备诊断
        设备：\(deviceName)
        ProductType：\(machine)
        芯片：\(chip)
        iOS：\(systemVersion)
        Build：\(buildVersion)
        目标设备型号匹配：\(isTargetModel ? "是" : "否")
        目标系统 Build 匹配：\(isTargetBuild ? "是" : "否")

        结论：设备信息匹配不代表存在可用越狱。当前项目不执行漏洞利用、不提权、不修改系统。
        目标：iPhone 12 / A14 / iOS 27.0 / 24A437
        """
    }
}

struct ResearchCheck: Identifiable {
    let id: String
    let title: String
    let status: String
    let detail: String
    let level: String
}

extension DeviceAudit {
    var checks: [ResearchCheck] {
        [
            .init(id: "target", title: "目标设备匹配", status: isTargetModel && isTargetBuild ? "完全匹配" : (isTargetModel ? "型号匹配" : "不匹配"), detail: "目标为 iPhone13,2 · A14 · iOS 27.0 · 24A437。当前：\(machine) / iOS \(systemVersion) / \(buildVersion)", level: isTargetModel && isTargetBuild ? "good" : "warning"),
            .init(id: "liter8", title: "Liter8", status: "未证实支持 A14", detail: "公开说明中的 iPhone 11 设备范围不能证明 iPhone 12/A14 兼容。", level: "warning"),
            .init(id: "usb", title: "usbliter8", status: "超出已列设备范围", detail: "已审阅的公开测试范围列出 A12/A13，未列出 A14。", level: "warning"),
            .init(id: "chain", title: "完整越狱链", status: "尚无可复现证据", detail: "尚未证实该精确设备与 Build 的 kernel、PPL/SPTM、代码签名绕过链。", level: "danger")
        ]
    }
}
