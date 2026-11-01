# IPA 构建说明（V1.3）

本项目不会要求你修改 iPhone 的系统设置，也不会安装描述文件、证书或越狱载荷。它是只读诊断应用。

## 重要限制

IPA 必须包含由 iOS SDK 编译出的 arm64 应用二进制，并由有效签名身份签名。当前制作环境没有 macOS、Xcode 或你的 Apple Developer 签名身份，因此不能诚实地把源码 ZIP 改名成 IPA，也不能在这里生成可安装的签名 IPA。

## 在 Mac 上一键构建

1. 解压本项目，在项目目录打开终端。
2. 安装并启动 Xcode，登录你的 Apple 开发者账号。
3. 找到 Apple Team ID（10 位字符）。
4. 执行：

```bash
chmod +x ./build_ipa.sh
./build_ipa.sh YOUR_TEAM_ID
```

也可以指定自己团队已注册的 Bundle ID：

```bash
./build_ipa.sh YOUR_TEAM_ID com.example.i12lab
```

成功后 IPA 位于 `build-ipa/export/`。

脚本使用 Ad Hoc 自动签名；设备需在该签名配置允许的设备范围内。签名是否可安装取决于证书、设备注册和 Apple 签名状态。该脚本不会连接或更改 iPhone。

## 在 Windows / iPhone 上

Windows 和 iPhone 本机不能替代 Xcode 完成 iOS 原生编译。可以把 ZIP 放到有 macOS + Xcode 的构建机上执行脚本，再把导出的 IPA 交给你现有的签名/安装流程。不要安装来源不明的企业证书或配置描述文件。
