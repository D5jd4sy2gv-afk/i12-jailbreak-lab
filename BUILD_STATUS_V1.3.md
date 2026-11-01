# V1.3 构建说明

- 版本：1.3（Build 13）
- 目标：iPhone 12 / iPhone13,2 / A14 / iOS 27.0 (24A437)
- 新增：通过 HTTPS 查询公开 IPSW 固件目录的轻量元数据。
- 本地导入：仍支持单独的 BuildManifest.plist。
- 限制：在线目录不提供独立 BuildManifest.plist；查询不等于本地清单字段验证，也不证明越狱兼容性。
- 安全：只读，不刷机、不恢复、不执行 exploit、不修改设备。

## 构建
使用 GitHub Actions 的 `Build unsigned iOS IPA` workflow。构建成功后从 Artifacts 下载 unsigned IPA，再使用用户自己的签名工具签名。不要将 P12 私钥或密码提交到仓库。
