# i12 Jailbreak Lab V1.3

只读 iOS 设备研究工具：设备识别、固件核对、公开证据审计和诊断报告导出。

## V1.3 新功能
- 在线查询 iPhone 12（iPhone13,2）固件目录，无需下载完整 IPSW。
- 显示版本、Build、签名标记、发布日期和文件大小。
- 保留独立 `BuildManifest.plist` 文件导入和本地字段核对。

在线数据来自 IPSW.me 公共固件目录 API，仅为第三方目录元数据。在线查询不会下载或提取 BuildManifest.plist。要逐字段核对 `ProductVersion`、`ProductBuildVersion` 和 `SupportedProductTypes`，仍需单独导入该 plist。

## 安全边界
本项目只读。不会执行漏洞利用、提权、修改启动链、关闭安全保护、刷机、恢复、抹除或写入设备。显示固件记录不代表存在可用越狱。

## 云端构建
使用仓库中的 GitHub Actions workflow 构建未签名 IPA。下载后需要使用自己的有效证书签名才能安装。请勿把证书私钥或密码提交到 GitHub。
