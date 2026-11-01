import SwiftUI
import UniformTypeIdentifiers

struct DashboardView: View {
    @State private var audit = DeviceAudit.collect()
    @State private var showAbout = false
    @State private var showReport = false
    @State private var showManifestImporter = false
    @State private var manifestResult: FirmwareManifestAudit?
    @State private var manifestError: String?
    @State private var firmwareCatalog: [FirmwareCatalogEntry] = []
    @State private var isLoadingCatalog = false
    @State private var catalogError: String?

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    header
                    deviceCard
                    firmwareCard
                    onlineFirmwareCard
                    statusCard
                    evidenceCard
                    evidenceLedgerCard
                    VStack(alignment: .leading, spacing: 10) {
                        Text("兼容性证据检查").font(.title3.bold())
                        ForEach(audit.checks) { check in CheckRow(check: check) }
                    }
                    actionCard
                    safetyCard
                }.padding()
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("i12 Jailbreak Lab")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button { audit = DeviceAudit.collect() } label: { Image(systemName: "arrow.clockwise") }
                    .accessibilityLabel("重新检测")
                }
            }
            .sheet(isPresented: $showAbout) { AboutView() }
            .sheet(isPresented: $showReport) { ReportView(text: audit.reportText + "\n\n" + (manifestResult?.summary ?? "尚未导入固件清单。")) }
            .fileImporter(isPresented: $showManifestImporter, allowedContentTypes: [.propertyList], allowsMultipleSelection: false) { result in
                do {
                    guard let url = try result.get().first else { return }
                    manifestResult = try FirmwareManifestAudit.inspect(url: url)
                    manifestError = nil
                } catch {
                    manifestResult = nil
                    manifestError = error.localizedDescription
                }
            }
        }
        .tint(.indigo)
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 7) {
            HStack {
                Image(systemName: "waveform.path.ecg.rectangle").font(.system(size: 30, weight: .semibold)).foregroundStyle(.indigo)
                Spacer()
                Text("V1.3 · READ ONLY").font(.caption.bold()).padding(.horizontal, 10).padding(.vertical, 6)
                    .background(Color.indigo.opacity(0.12)).clipShape(Capsule())
            }
            Text("设备研究工具箱").font(.largeTitle.bold())
            Text("设备识别、固件核对、证据审计与诊断报告导出。")
                .font(.subheadline).foregroundStyle(.secondary)
        }
    }

    private var deviceCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("当前设备", systemImage: "iphone").font(.headline)
            infoLine("设备名称", audit.deviceName)
            infoLine("设备标识", audit.machine)
            infoLine("处理器", audit.chip)
            infoLine("iOS 版本", audit.systemVersion)
            infoLine("Build 版本", audit.buildVersion)
            Divider()
            HStack {
                Text("目标设备")
                Spacer()
                Text(audit.isTargetModel && audit.isTargetBuild ? "完全匹配" : "未完全匹配")
                    .font(.caption.bold()).foregroundStyle(audit.isTargetModel && audit.isTargetBuild ? .green : .orange)
            }
        }.padding().background(.background).clipShape(RoundedRectangle(cornerRadius: 18))
    }

    private var firmwareCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("固件清单核对", systemImage: "doc.badge.gearshape").font(.headline)
            Text("导入从 IPSW 中提取的 BuildManifest.plist，检查它是否包含 iPhone13,2，以及 Build 是否为 24A437。不会刷机或修改设备。")
                .font(.caption).foregroundStyle(.secondary)
            Button { showManifestImporter = true } label: {
                Label("选择 BuildManifest.plist", systemImage: "folder")
                    .frame(maxWidth: .infinity).padding(12)
                    .background(Color.indigo.opacity(0.12)).clipShape(RoundedRectangle(cornerRadius: 12))
            }.buttonStyle(.plain)
            if let result = manifestResult {
                Divider()
                infoLine("固件版本", result.productVersion)
                infoLine("Build", result.buildVersion)
                infoLine("包含 iPhone13,2", result.matchesTargetModel ? "是" : "否")
                infoLine("目标 Build 匹配", result.matchesTargetBuild ? "是" : "否")
                Text("此结果仅核对固件元数据，不代表越狱支持。")
                    .font(.caption).foregroundStyle(.secondary)
            }
            if let error = manifestError {
                Text(error).font(.caption).foregroundStyle(.red)
            }
        }.padding().background(.background).clipShape(RoundedRectangle(cornerRadius: 18))
    }

    private var onlineFirmwareCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("在线固件目录（轻量查询）", systemImage: "globe.americas").font(.headline)
            Text("只查询 iPhone13,2 的固件版本、Build、签名状态和文件大小等目录信息，不下载 IPSW，不消耗 10GB 流量。")
                .font(.caption).foregroundStyle(.secondary)
            Button {
                Task {
                    isLoadingCatalog = true
                    catalogError = nil
                    do {
                        firmwareCatalog = try await FirmwareCatalogService.fetch()
                    } catch {
                        catalogError = error.localizedDescription
                    }
                    isLoadingCatalog = false
                }
            } label: {
                HStack {
                    if isLoadingCatalog { ProgressView().padding(.trailing, 4) }
                    Label(isLoadingCatalog ? "正在查询…" : "查询 iPhone 12 固件目录", systemImage: "arrow.down.circle")
                    Spacer()
                }
                .frame(maxWidth: .infinity).padding(12)
                .background(Color.indigo.opacity(0.12)).clipShape(RoundedRectangle(cornerRadius: 12))
            }
            .buttonStyle(.plain).disabled(isLoadingCatalog)

            if !firmwareCatalog.isEmpty {
                let target = firmwareCatalog.first { $0.buildid == audit.buildVersion }
                VStack(alignment: .leading, spacing: 7) {
                    if let target {
                        Label("找到当前 Build：\(target.version)（\(target.buildid)）", systemImage: "checkmark.circle.fill")
                            .font(.subheadline.bold()).foregroundStyle(.green)
                        Text("\(target.signingLabel) · IPSW 大小：\(target.sizeLabel)")
                            .font(.caption).foregroundStyle(.secondary)
                    } else {
                        Label("目录中未找到当前 Build：\(audit.buildVersion)", systemImage: "exclamationmark.triangle")
                            .font(.subheadline.bold()).foregroundStyle(.orange)
                    }
                    Divider()
                    ForEach(firmwareCatalog.prefix(6)) { item in
                        VStack(alignment: .leading, spacing: 3) {
                            HStack {
                                Text("iOS \(item.version) · \(item.buildid)").font(.subheadline.weight(.medium))
                                Spacer()
                                Text(item.signed == true ? "Signed" : (item.signed == false ? "Unsigned" : "Unknown"))
                                    .font(.caption2.bold()).foregroundStyle(item.signed == true ? .green : .secondary)
                            }
                            Text("\(item.signingLabel) · \(item.sizeLabel) · \(item.releasedate ?? "日期未知")")
                                .font(.caption2).foregroundStyle(.secondary)
                        }
                        if item.id != firmwareCatalog.prefix(6).last?.id { Divider() }
                    }
                }
            }
            if let catalogError {
                Text(catalogError).font(.caption).foregroundStyle(.red)
            }
            Text("数据来自第三方公开固件目录，仅供核对。在线结果不是 BuildManifest.plist，也不代表 Apple 签名状态的实时保证；需要逐字段验证时仍需导入独立清单文件。")
                .font(.caption2).foregroundStyle(.tertiary)
            Link("打开 iPhone 12 固件目录", destination: URL(string: "https://ipsw.me/iPhone13%2C2")!)
        }.padding().background(.background).clipShape(RoundedRectangle(cornerRadius: 18))
    }

    private var evidenceCard: some View {
        VStack(alignment: .leading, spacing: 9) {
            Label("公开证据与核验入口", systemImage: "checkmark.seal").font(.headline)
            Text("Liter8 项目设备表：iPhone 11 有测试记录；iPhone 11 Pro / Pro Max 为实验性记录。没有列出 iPhone 12 / A14 的成功测试。")
                .font(.caption).foregroundStyle(.secondary)
            Link("查看 Liter8 官方仓库", destination: URL(string: "https://github.com/Xplo8E/Liter8")!)
            Link("查看 Apple Wiki 越狱状态", destination: URL(string: "https://theapplewiki.com/wiki/jailbreak")!)
            Link("查看 iPhone 12 / iOS 27.0 固件信息", destination: URL(string: "https://www.applefirmwares.com/firmware/iPhone13%2C2/27.0")!)
            Text("证据快照：2026-11-01。第三方项目状态可能变化；以项目维护者最新发布和可复现测试为准。")
                .font(.caption2).foregroundStyle(.tertiary)
        }.padding().background(.background).clipShape(RoundedRectangle(cornerRadius: 18))
    }

    private var evidenceLedgerCard: some View {
        VStack(alignment: .leading, spacing: 11) {
            Label("证据数据库 · \(EvidenceDatabase.snapshotDate)", systemImage: "books.vertical").font(.headline)
            Text("目标：\(EvidenceDatabase.target)").font(.caption).foregroundStyle(.secondary)
            ForEach(EvidenceDatabase.records) { record in
                VStack(alignment: .leading, spacing: 5) {
                    HStack(alignment: .firstTextBaseline) {
                        Text(record.title).font(.subheadline.bold())
                        Spacer()
                        Text(record.status).font(.caption.bold()).foregroundStyle(.orange)
                    }
                    Text(record.detail).font(.caption).foregroundStyle(.secondary)
                    Link("打开来源 · 置信度：\(record.confidence)", destination: record.url).font(.caption)
                }
                if record.id != EvidenceDatabase.records.last?.id { Divider() }
            }
            Text("数据库是带日期的公开资料快照，不是漏洞利用代码，也不构成对设备兼容性的保证。")
                .font(.caption2).foregroundStyle(.tertiary)
        }.padding().background(.background).clipShape(RoundedRectangle(cornerRadius: 18))
    }

    private var statusCard: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: "exclamationmark.shield.fill").font(.title2).foregroundStyle(.orange)
            VStack(alignment: .leading, spacing: 5) {
                Text("越狱可用性：尚未验证").font(.headline)
                Text("当前没有足够的公开、可复现证据证明 iPhone 12 / A14 / iOS 27.0 (24A437) 可完成完整越狱。")
                    .font(.subheadline).foregroundStyle(.secondary)
            }
        }.padding().frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.orange.opacity(0.09)).clipShape(RoundedRectangle(cornerRadius: 18))
    }

    private var actionCard: some View {
        VStack(spacing: 10) {
            Button { showReport = true } label: {
                Label("查看 / 分享诊断报告", systemImage: "square.and.arrow.up")
                    .frame(maxWidth: .infinity).padding()
                    .background(Color.indigo).foregroundStyle(.white).clipShape(RoundedRectangle(cornerRadius: 14))
            }
            Button { showAbout = true } label: {
                Label("项目说明与限制", systemImage: "info.circle")
                    .frame(maxWidth: .infinity).padding()
                    .background(Color(.secondarySystemBackground)).clipShape(RoundedRectangle(cornerRadius: 14))
            }.buttonStyle(.plain)
        }
    }

    private var safetyCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("安全边界", systemImage: "lock.shield").font(.headline)
            Text("本版本只读取公开系统标识并展示研究证据。不会执行漏洞利用、提权、修改启动链、关闭安全保护或写入设备。")
                .font(.subheadline).foregroundStyle(.secondary)
            Text("请勿为测试而更新、抹除或恢复设备，也不要安装来源不明的描述文件、证书或 IPA。")
                .font(.subheadline.bold())
        }.padding().frame(maxWidth: .infinity, alignment: .leading)
            .background(.background).clipShape(RoundedRectangle(cornerRadius: 18))
    }

    private func infoLine(_ title: String, _ value: String) -> some View {
        HStack { Text(title).foregroundStyle(.secondary); Spacer(); Text(value).fontWeight(.medium).textSelection(.enabled) }
            .font(.subheadline)
    }
}

private struct CheckRow: View {
    let check: ResearchCheck
    private var color: Color {
        switch check.level { case "good": return .green; case "danger": return .red; default: return .orange }
    }
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline) {
                Text(check.title).font(.headline)
                Spacer()
                Text(check.status).font(.caption.bold()).foregroundStyle(color)
            }
            Text(check.detail).font(.caption).foregroundStyle(.secondary)
        }.padding().frame(maxWidth: .infinity, alignment: .leading)
            .background(.background).clipShape(RoundedRectangle(cornerRadius: 14))
    }
}

private struct ReportView: View {
    @Environment(\.dismiss) private var dismiss
    let text: String
    var body: some View {
        NavigationStack {
            ScrollView { Text(text).font(.system(.body, design: .monospaced)).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading).padding() }
                .navigationTitle("诊断报告").navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .topBarLeading) { ShareLink(item: text) }
                    ToolbarItem(placement: .topBarTrailing) { Button("完成") { dismiss() } }
                }
        }
    }
}

private struct AboutView: View {
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        NavigationStack {
            List {
                Section("当前版本") { LabeledContent("版本", value: "1.3"); LabeledContent("目标", value: "iPhone 12 / A14 / 24A437") }
                Section("说明") {
                    Text("V1.3 新增在线固件目录轻量查询，并保留 BuildManifest.plist 本地导入与证据数据库。证据按设备型号、芯片和 Build 分开记录，避免把其他机型的测试结果误认为本机支持。")
                    Text("这是只读研究工具箱。越狱状态不能仅凭文件存在、设备型号或系统版本推断。兼容性必须由精确设备与 Build 上可复现的技术证据支持。")
                    Text("固件清单导入功能只接受 BuildManifest.plist；需先从 IPSW 容器中提取该文件。在线目录只返回版本、Build、签名状态和文件大小等元数据，不会下载完整 IPSW 或自动提取 BuildManifest.plist。IPA 需要在 macOS 上使用 Xcode 编译，并通过有效的开发者签名或适用的侧载方式安装。本源码包不是已签名 IPA。")
                }
            }.navigationTitle("项目说明").toolbar { ToolbarItem(placement: .topBarTrailing) { Button("完成") { dismiss() } } }
        }
    }
}
