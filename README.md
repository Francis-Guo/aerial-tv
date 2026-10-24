# Aerial 自用维护版

基于 [pengchujin/aerial-tv](https://github.com/pengchujin/aerial-tv) 的电视桌面。维护分支为 `fei-managed`，起点固定为 `6b398b7c4e4251da764ab88b8f5973e59c603ae3`（v1.42）。

本分支保留桌面、应用排列、输入源、壁纸与屏保等功能，删除应用内版本检查、APK 下载与安装入口。`tools/get.sh` 和 `tools/install.sh` 已禁用；更新由设备所有者审查、构建、验签后通过官方 ADB 安装。

- [构建、安装、回退和后续维护](docs/MANAGED-BUILD.zh-CN.md)
- [维护签名的公开 SHA-256 指纹](docs/managed-signing-certificate.sha256)
- [APK 核验脚本](tools/verify-managed-apk.py)
- [上游功能说明存档](docs/UPSTREAM-README.md)（其中远程安装与发布流程不适用于本分支）

当前自用版本 `1.42-fei.2`（versionCode 47），最低 Android 5.0 / API 21。Release 必须使用所有者保管的独立签名，不回退到 debug 签名。

`keep_adb` 默认关闭，可以经所有者批准配置自动恢复；它保留系统电脑授权校验，不保证所有厂商固件都能恢复网络调试。已安装设备的实际配置记录保存在被 Git 忽略的 `local/` 中。

上游有新版本时不自动同步、构建或安装。天气、壁纸、手机配置页仍属于外部输入面；关闭软件更新不等于完全离线或零风险。Netflix 和 YouTube 的系统、设备认证与播放兼容性需单独确认。

原作者与许可证见 [上游仓库](https://github.com/pengchujin/aerial-tv) 及本仓库保留的许可证文件。
