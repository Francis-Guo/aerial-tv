# Aerial 自用维护分支

仓库 `Francis-Guo/aerial-tv`，维护分支 `fei-managed`，上游基线 `6b398b7c4e4251da764ab88b8f5973e59c603ae3`。
本分支维护说明见 `docs/MANAGED-BUILD.zh-CN.md`。`docs/HANDOFF.md`、`docs/ARCHITECTURE.md` 和机型资料保留上游历史内容，涉及更新器、远程脚本与其他家庭设备的描述不代表本分支的当前行为或实测结果。

## 当前实现

- Kotlin / Compose；`standard` flavor 声明 HOME，`guard` flavor 不声明 HOME。
- minSdk 21，targetSdk 34，compileSdk 36；使用 JDK 17、Build Tools 35.0.0、Gradle 8.14.3。
- 应用内版本检查、APK 下载与安装入口已删除；`tools/get.sh` 与 `tools/install.sh` 会明确退出。
- Release 必须读取被忽略的 `local/signing.properties`，不得回退到 debug 签名。
- `docs/managed-signing-certificate.sha256` 是本地维护签名的公开指纹。
- `keep_adb` 默认 false；可经受 `WRITE_SECURE_SETTINGS` 保护的配置广播显式启用。
- `local/` 存放私钥、密码、电视地址与安装前后快照，不进入 Git。

## 验证命令

```sh
./gradlew --no-daemon testStandardReleaseUnitTest lintStandardRelease assembleStandardRelease
python3 tools/verify-managed-apk.py app/build/outputs/apk/standard/release/app-standard-release.apk --build-tools "$ANDROID_HOME/build-tools/35.0.0" --expected-cert-sha256 "$(cat docs/managed-signing-certificate.sha256)"
```

依赖校验元数据只在审查新依赖后有意更新。普通构建不得使用 `--write-verification-metadata` 自动信任变化。
部署仅使用已核验本地 APK 与官方 ADB；设备具体状态以 `local/TVS.md` 和快照为准。
保留 `com.mitv.tvhome` 与已有无障碍服务；精确恢复原值，不直接运行上游通用恢复脚本。

## 代码约定

- 注释和标识符用英文，界面文字放 `res/values`（英文）、`res/values-zh`（中文）、`res/values-ru`（俄语）、`res/values-uk`（乌克兰语）、`res/values-kk`（哈萨克语），五份都要加，占位符要一致。手机设置页 `assets/web/index.html` 的文字在 `KEYS` / `TEXTS` 表里，同样五种语言，脚本里不要写死文字。
- 界面按 960×540dp 的画布设计（`MainActivity` 统一缩放），不要按真实 dpi 计算。
- 动效：使用 `ui/theme/Theme.kt` 里的 `Motion` 曲线；会被打断的动画（比如焦点）用 spring；不在空闲时跑持续动画；每帧最多一次全屏绘制。
- 遥控器可按的控件用 `ui/components/Pressable`，它只在「本控件上开始的按压」抬起时触发，这样长按打开菜单时，那次抬起不会误触菜单的第一项。
- 厂商的特殊处理写成按功能检测（看包是否存在、设置是否存在），并在注释里写明是哪台机型上验证的。只有确实无法检测时，才写进 `DeviceProfile` 按机型硬编码。
