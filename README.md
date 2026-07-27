# Mimonitor Toolbox (macOS 版)

> 本项目 Fork 自 [YiHooong/Mimonitor_Toolbox](https://github.com/YiHooong/Mimonitor_Toolbox)，
> 在原项目基础上移植并适配了 macOS（自动启动、内置 adb、`.app` 打包、原生标题栏按钮等），
> 让原本仅支持 Windows 的桌面工具也能在 Mac 上运行。核心功能、实现原理与创意均来自原项目，
> 相关 credit 归原作者所有；如需 Windows 版本请前往原仓库获取。

Redmi G Pro 27U 2026显示器 ADB 控制工具
测试机器系统版本号：HyperOS 3.0.112.0  
不确定小米是否后续会对该行为进行阻止 且用且珍惜吧 尚不知2025是否可用  
摸索了很久 有点地方写的也不怎么样 有问题欢迎issue  
如果觉得本项目对你有帮助，欢迎点亮一颗 ⭐ (Star) 支持一下！或者，您也可以通过赞助 Sponsor 请我喝杯快乐水。开源不易，感谢认可！🙌  

<img src="assets/e41e5c8458c34a6e2f7c46b92be05381.png" width="300"> <img src="assets/116be2f82c8a3f88e57f95cf4f11c0a9.jpg" width="300">

## 软件截图

<img src="assets/Screensettings.png" width="500">
<img src="assets/Gamesettings.png" width="500">

## 实现原理

通过无线 ADB 连接到显示器内置的 Android 系统，利用 `settings` 命令和 MTK 平台 JNI 接口（`MtkDirectTool.jar`）直接读写硬件寄存器，实现对显示器各项参数的精确控制。

### 通信架构

```
PC (MonitorToolbox.exe)
  │
  ├─ ADB Wireless ──► 显示器 Android 系统 (port 5555)
  │
  ├─ settings get/put ──► 读写 Android Global Settings
  │   (picture_mode, picture_backlight, picture_contrast, ...)
  │
  └─ MtkDirectTool.jar ──► MTK JNI 直写硬件寄存器
      (背光 g_disp__disp_back_light)
      (色温 g_video__clr_temp)
      (色域 g_video__vid_gamut_mapping_mode)
      (精密控光 g_video__vid_local_dimming)
      (320Hz g_fusion_picture__hdmi_edid_version)
      (FreeSync g_video__freesync_switch)
      (恢复默认 g_fusion_picture__pic_reset_def_bypicmode)

  └─ ColorfulLedTool.jar ──► MiTV PM2 炫彩灯 HIDL 接口
      (炫彩灯模式)
      (照明色温)
      (纯色颜色)
      (亮度)
```

### JNI 调用方式

通过 `service call TvService` 调用系统服务，以 `app_process` 执行 jar 包中的 Java 类：

```bash
# 读取寄存器
service call TvService 3 s16 "sh -c eval\${IFS}CLASSPATH=/data/data/mitv.service/cache/MtkDirectTool.jar\${IFS}/system/bin/app_process\${IFS}/data/data/mitv.service/cache\${IFS}MtkDirectTool\${IFS}get\${IFS}g_disp__disp_back_light"

# 写入寄存器
service call TvService 3 s16 "sh -c eval\${IFS}CLASSPATH=...\${IFS}MtkDirectTool\${IFS}set\${IFS}g_disp__disp_back_light\${IFS}50\${IFS}3"
```

单项兼容读取仍可通过 `logcat` 获取结果；页面刷新使用 `batchGet` 一次读取多个寄存器，
结果写入 `/sdcard/Download/Mimonitor_Toolbox/.mtk_batch_result.txt` 后由桌面端解析。

### 数据加载策略

采用按需加载，不持续轮询：

1. **首次进入页面** — 读取该页面所有 settings key + JNI 寄存器，显示 loading 遮罩
2. **再次进入** — 直接使用缓存数据，不重新读取
3. **手动刷新** — 点击"刷新数据"按钮强制重新读取
4. **模式切换** — 自动刷新当前页面数据

### Jar 自动部署

首次连接时自动检测并补齐 `MtkDirectTool.jar` / `ColorfulLedTool.jar`：

1. 检查设备 `/sdcard/` 中的 jar 大小是否与本地一致
2. 缺失或大小不一致时从本地 push 到 `/sdcard/`
3. 从 `/sdcard/` 复制到 `/data/data/mitv.service/cache/`

打包后 jar 会从 `assets/runtime/` 嵌入 exe 中（PyInstaller `--add-binary`）。

## 功能

- 无线 ADB 连接，内网设备自动扫描
- 画面设置：模式 / 背光 / 黑色级别 / 对比度 / 饱和度 / 色调 / 锐度 / 色温 / 精密控光 / 动态清晰度 / 响应时间 / 色域
- 游戏模式：准星 / 动态准星 / 狙击镜 / 夜视 / 320Hz / FreeSync / FPS 计数器 / 秒表 / 定时器
- 信号源切换（HDMI 1/2 / DP / USBC）
- 屏幕灯：炫彩灯模式 / 亮度挡位 / 纯色颜色 / 照明色温
- 虚拟遥控器
- 全局快捷键（Windows）+ OSD 悬浮通知
- 开机自启动最小化
- 4K UI 模式（3840×2160 / DPI 640，需重启显示器）
- ADB 保活守护部署与状态检测（内置 `assets/adb_guardian/adbguardian-signed.apk`）
- 操作日志记录与导出

## 项目资源结构

```text
assets/
  app/
    icon.ico   # Windows
    icon.icns  # macOS
  runtime/
    adb.exe / AdbWinApi.dll / AdbWinUsbApi.dll  # Windows
    adb                                          # macOS (universal arm64 + x86_64)
    MtkDirectTool.jar
    ColorfulLedTool.jar
  adb_guardian/
    adbguardian-signed.apk
tools/
  colorful_led/
    ColorfulLedTool.java
```

`assets/runtime/` 是主程序运行所需的本地工具，`assets/adb_guardian/` 是可部署到显示器端的 ADB 保活应用，`tools/colorful_led/` 保留屏幕灯 helper 源码。

## 打包

### Windows

```bash
# 安装锁定的构建依赖
python -m pip install -r requirements-build.txt

# 使用与 build.bat、GitHub Actions 相同的资源清单打包
python -m PyInstaller --clean --noconfirm MonitorToolbox.spec
```

### macOS

```bash
./build_mac.sh
# 等价于:
#   python3 -m pip install -r requirements-build.txt
#   python3 -m PyInstaller --clean --noconfirm MonitorToolbox.mac.spec
```

产物为 `dist/MonitorToolbox.app`。由于未做 Apple 签名/公证，首次打开时 Gatekeeper 会拦截，
需在 Finder 中右键 `MonitorToolbox.app` → 打开，在弹出的对话框中确认打开。

## macOS 从源码运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install PyQt6==6.11.0 PyQt6-Fluent-Widgets==1.11.2 PyQt6-Frameless-Window==0.8.1
python3 monitor_controller.py
```

`assets/runtime/adb` 已内置 macOS 通用二进制（arm64 + x86_64），无需另装 ADB。

macOS 已知限制：
- 全局快捷键（`RegisterHotKey`）目前仅在 Windows 上实现，macOS 版本暂不支持系统级全局热键，
  应用内的按钮/菜单操作不受影响。
- HDR 状态读取（DXGI）为 Windows 专属探测手段，macOS 上会跳过该项检测。

## 依赖

- Python 3.10+
- PyQt6（版本见 `requirements-build.txt`）
- PyQt-Fluent-Widgets（版本见 `requirements-build.txt`）
- ADB（打包进 exe / .app，无需额外安装）

## 感谢认可！🙌
