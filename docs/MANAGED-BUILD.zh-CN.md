# Aerial 自用维护版本

维护仓库：`Francis-Guo/aerial-tv`，分支 `fei-managed`。
初始上游基线：`pengchujin/aerial-tv@6b398b7c4e4251da764ab88b8f5973e59c603ae3`（v1.42）。
自用版本：`1.42-fei.2`，versionCode `47`，包名保持 `app.orchard.tv`。

## Android 6 桌面回退修复（1.42-fei.2）

MiTV4-ANSM0 / Android 6.0.1 在首次安装并开启守护服务后，曾出现 Home 键可用，但应用退出后落到原厂桌面的情况。服务仍在运行；重连无障碍总开关后，日志记录到原厂桌面的窗口事件并成功接管。原实现只在开机前三分钟检查“已连接却收不到窗口事件”，会漏掉安装或稍后重连。

此版本对 Android 6 及以下的每次服务连接都安排现有的 20 秒检查；收到事件则不处理，无事件时最多每进程重连一次。保持已有无障碍服务列表，短暂关闭再恢复总开关的行为与上游已有自愈逻辑一致。未新增权限，未禁用原厂桌面。

诊断命令：

```sh
adb shell dumpsys activity service app.orchard.tv/.guard.HomeGuardService
```

可查看 `sawEvent`、`windowEventCount`、`deafRetried` 与 `lastWindow`，不会读取窗口文字。该修复针对已观察到的事件丢失；待机、重启和各应用的退出路径需要分别验收。

## 已做修改

- 删除应用内版本检查、APK 下载和更新页面，以及 `check_update` / `update_test` 广播处理。
- 删除安装 APK 的权限声明、更新 FileProvider 和文件路径配置。
- 设置页保留电视系统设置入口，移除指向上游远程安装命令的二维码。
- `tools/get.sh`、`tools/install.sh` 拒绝执行，防止误用上游下载与自动授权流程。
- Gradle 分发包固定 SHA-256；依赖校验记录随本分支维护。
- Release 构建要求 `local/signing.properties`，缺失时失败，不回退到 debug 签名。
- 修正上游现有 lint 声明问题：Media3 局部 opt-in、品牌名不翻译标记、HOME flavor 显式 exported；遥控器回调保留原行为，对 AndroidX Core 桥接方法的 RestrictedApi 报告作方法级说明和抑制。

桌面仍包含天气、在线壁纸和按需开启的手机配置页；这是关闭远程软件更新的版本，不是完全离线版本。

## 本地密钥与构建

`local/` 被 Git 忽略。私钥、密码、电视地址、配置快照保存在该目录，不推送到 GitHub。
Git 忽略不阻止 macOS 对工作目录进行云同步；应按自己的备份策略保护整个签名目录。
签名配置格式沿用项目的 `storeFile`、`storePassword`、`keyAlias`、`keyPassword`。
必须备份密钥和密码到自己的安全存储；丢失密钥将不能给现有安装做同签名覆盖升级。

使用 JDK 17、Android SDK platform 36、Gradle wrapper。首次安装 SDK 需要设备所有者接受 Google 的 SDK 许可协议。

```sh
./gradlew --no-daemon testStandardReleaseUnitTest lintStandardRelease assembleStandardRelease
```

构建使用固定依赖校验记录。引入新依赖或合并上游后应先审查来源和版本，再有意更新校验记录；不要在日常构建中自动重建白名单。
校验记录首次采集基于 HTTPS 官方仓库，提供后续漂移检测，不等于对依赖代码进行完整审计。

## 安装与回退

使用官方 Android SDK 的 `apksigner` 验证 APK 签名，使用 `aapt2 dump badging` 验证包名、minSdk、版本号，记录 SHA-256。
检查打包后的 Manifest 不含 `REQUEST_INSTALL_PACKAGES` / 更新 FileProvider，DEX 不含旧更新器地址。

```sh
python3 tools/verify-managed-apk.py app/build/outputs/apk/standard/release/app-standard-release.apk \
  --build-tools "$ANDROID_HOME/build-tools/35.0.0" \
  --expected-cert-sha256 "$(cat docs/managed-signing-certificate.sha256)"
```

证书指纹是公开信息；它固定本分支首次安装的签名身份。此检查不是对 APK 所有行为的安全证明。

只将已核验的本地 APK 通过官方 ADB 安装。不要执行仓库原有远程一键命令。
安装前保留 HOME、无障碍服务列表、屏保设置与应用安装状态；保留原厂桌面及已有无障碍服务。
先验证桌面启动、遥控器、应用启动和 HDMI，再按实测需求设置默认 HOME 或桌面守护。
`keep_adb` 默认关闭；只有设备所有者明确选择常开维护时才启用。常驻授权必须在本机维护记录中说明必要性及恢复原值的方法。

恢复优先使用安装前的原值；上游 `restore.sh` 包含通用默认值推断，不能代替设备快照。
低版本 APK 可能无法直接降级，不要通过卸载来掩盖签名或版本问题，卸载会清除应用数据。

## 后续修改

1. 固定上游提交并审查差异，不自动同步、构建或部署上游。
2. 保留本分支的软件更新禁用约束；重复检查 Manifest、DEX 和入口。
3. 修改后增加自用版本和 versionCode，始终使用相同本地密钥。
4. 通过构建、相关测试和设备验证后，才用本地 APK 覆盖安装。

`docs/HANDOFF.md` 是上游历史资料，其中的电视地址示例、安装脚本、发布方式和测试记录不代表本分支已经执行或验证。

## ADB 与以后更新

ADB 是电视系统的调试功能，不属于 Aerial。自用版保留可选的 `keep_adb`，默认 `false`。
开启后，守护在取得 `WRITE_SECURE_SETTINGS` 权限且能运行时，将 `Settings.Global.ADB_ENABLED` 写回 `1`；不修改电脑授权校验，不执行远程脚本。
它并不保证任意固件、待机或进程被停止时都能恢复网络 ADB；本机行为必须实测。

平时关闭 ADB 时，以后在电视设置中重新打开之前使用的 ADB / USB 调试开关，电脑和电视连接同一局域网，提供当前 IP，按需在电视上允许本电脑。ADB 已关闭时，电脑无法通过这条已关闭的连接远程开启它。
若开启自动恢复，再要关闭 ADB，应先关闭 `keep_adb`，否则守护可能写回开启状态。

仅在设备所有者明确批准后使用以下配置（`<电视地址>` 由本地记录提供）：

```sh
adb -s <电视地址> shell am broadcast -a app.orchard.tv.CONFIG -n app.orchard.tv/.guard.ConfigReceiver --ez keep_adb true
# 取消自动恢复：
adb -s <电视地址> shell am broadcast -a app.orchard.tv.CONFIG -n app.orchard.tv/.guard.ConfigReceiver --ez keep_adb false
```

电脑授权仍由系统管理。只授权自己的电脑，不将 ADB 端口暴露到公网。常开会增加旧系统调试服务的暴露时间，不能因自用签名而视为零风险。

## 本机构建路径

若 Documents 下出现 macOS `dataless` 文件、Gradle 长时间卡在源码读取，可把固定源码和修改复制到非云同步目录编译，并使用独立 `GRADLE_USER_HOME`。先逐文件校验复制内容，完成后将校验元数据、APK 与验证结果同步回维护仓库/交付目录。临时目录不能作为签名密钥的唯一存放位置。

## 构建检查记录（2026-10-24）

- 自用版发布构建、20 项单元测试通过；lint 为 0 错误、105 警告、3 提示。警告仍需按后续修改范围维护，不能把构建成功当作完整安全认证。
- APK 使用独立 RSA 3072 签名；v1 与 v2 验签通过，支持 Android 6 的 v1 验签路径。
- 核验包名、minSdk 21、ARMv7，以及 Manifest 和 DEX 中已移除更新入口的相关标记；错误证书指纹会被核验脚本拒绝。
- 依赖校验记录覆盖 502 个组件（首次采集），使用 SHA-256；首次信任建立在官方 HTTPS 仓库上。
- 这份记录不代替电视实测；设备的安装、授权、按键、待机等结果另记在本机 `local/TVS.md`。
