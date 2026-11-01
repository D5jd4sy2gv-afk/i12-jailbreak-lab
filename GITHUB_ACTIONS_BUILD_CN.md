# GitHub 云端构建 IPA（中文说明）

本项目已附带 `.github/workflows/build-unsigned-ipa.yml`。GitHub Actions 会在 macOS 运行器上调用 Xcode 编译 iOS App，并把 `.app` 打包为未签名 IPA。

## 操作步骤

1. 将本目录中的**全部文件和隐藏目录 `.github`** 上传到 GitHub 仓库根目录（不要只上传里面的源码文件）。
2. 打开仓库的 **Actions** 页面。
3. 首次使用时，若页面提示启用 Actions，选择允许。
4. 在左侧选择 **Build unsigned iOS IPA**，点击 **Run workflow**，再点击绿色的 **Run workflow**。
5. 等待任务完成，打开成功的运行记录，在 **Artifacts** 区域下载 `i12-Jailbreak-Lab-unsigned-IPA`。
6. 解压下载的 artifact ZIP，取出 `i12_Jailbreak_Lab-unsigned.ipa`，再交给易签使用你自己的证书签名安装。

## 重要说明

- 该工作流只编译和打包，不会自动签名；因此不能把未签名 IPA 直接当作已可安装成品。
- 不要把 Apple 证书私钥、P12 密码、Provisioning Profile 或其他签名凭据提交到公开仓库或写进源码。
- 易签签名时，使用与你的证书/描述文件匹配的 Bundle ID：`com.research.i12jailbreaklab`。如果证书不允许该标识，需要在 Xcode 项目中改为已授权的 Bundle ID 后重新构建。
- 如果 Actions 失败，下载构建日志 `xcodebuild.log`，根据第一条 `error:` 定位；不要只看最后的 `BUILD FAILED`。
- 本应用是只读设备/固件研究诊断工具，不是越狱程序；不会利用漏洞、绕过系统防护或修改设备。
