# Sunshine macOS 压感笔与单指触控补丁

[English](README.en.md) · [安装指南](docs/INSTALL.md) · [测试与限制](docs/TESTING.md)

让远程连接 Mac 的触控笔保留压感，并让手指可以点击菜单、拖动窗口。

这是基于 **Sunshine + libvirtualhid** 的独立社区补丁仓库，不是上游官方发行版。仓库提供源码补丁和复现步骤，不提供预编译安装包。适合能在 Mac 上编译 Sunshine 的用户。

**2026-10-24 实测：压感绘画、手指点击和拖动可同时正常使用。** 服务端为 Intel NUC8i7BEH / macOS 26.7.1，绘画使用 Krita 5.3.4.1，主虚拟显示器启用 HiDPI。其他 Mac 和应用的兼容性需要验证。

## 能做什么

- **压感笔输入**：通过 CoreGraphics 数位笔事件传递压力、工具身份、倾斜和侧键状态。压力绘画已真实设备验证；倾斜、橡皮擦和侧键仅有自动测试/本地事件转换验证。
- **单指点击与拖动**：没有原生触摸屏后端时，把第一根手指映射为鼠标左键；额外手指不会抢占拖动。
- **笔优先**：落笔时释放手指模拟按键；笔接触期间不接受新的手指拖动。这是软件状态判断，不是硬件手掌识别。
- **输入状态清理**：取消、断连、销毁客户端时清理相应状态，减少残留按键问题。
- **HiDPI 坐标处理**：笔输入使用屏幕逻辑尺寸与原点；侧键专用包不会覆盖正在绘画的位置和压力。

不实现系统原生多点触摸、双指缩放/旋转/滚动、长按右键或物理 HID 数位板注册。单指映射当前使用**主显示器**；多屏、旋转屏和其他缩放组合尚未完成验收。

## 使用路线

1. 按下表检出固定版本的 Sunshine 并初始化子模块。
2. 用 `scripts/apply-patches.py` 校验并应用 **两个运行时补丁**。
3. 在 macOS 上编译程序和 Web UI，打包成独立的 `Sunshine Pen Touch.app`。
4. 为新应用授予辅助功能与录屏权限，停止原 Sunshine 后试运行。
5. 验证压感和手指操作；出现问题可退出测试版并恢复原版。

完整命令见 **[安装指南](docs/INSTALL.md)**。不要把这组补丁直接应用到任意最新版本，也不要把三个补丁全部打到同一个仓库。

## 版本与补丁

| 文件 | 适用基线 | 用途 |
| --- | --- | --- |
| `patches/sunshine-pen-integration.patch` | Sunshine `63d35f702ee9e362e43263742981836ec0710384`（v2026.914.233613） | 运行时：HiDPI、侧键、单指映射与清理 |
| `patches/sunshine-pinned-libvirtualhid-backport.patch` | Sunshine 子模块 `53e1a949fc0784af716b782ddfa6c647cafd1f05` | 运行时：当前固定依赖的 macOS 笔后端 |
| `patches/libvirtualhid-macos-pen.patch` | 独立 libvirtualhid `45c9b4db05779d18224a751e33cb8dfea78201bb` | 开发者：后端、库测试与文档；不是第三个运行时补丁 |

补丁摘要与基线记录在 [manifest.json](patches/manifest.json)。脚本先校验两个目标的版本、摘要和可应用性，再修改文件；重复执行会识别已应用状态，不重置仓库。

## 验证与反馈

库测试 139 通过、2 项 Linux 硬件测试跳过；最终 Sunshine 设备/会话筛选测试 22 通过。真实用户确认压感、手指点击与拖动正常。详见 [测试记录](docs/TESTING.md)，不将本地事件转换测试当作完整设备验收。

反馈请说明 Mac 架构、macOS 版本、补丁基线、屏幕缩放、绘画应用，以及“光标不动 / 只有普通鼠标事件 / 有 Tablet 事件但笔刷不变粗”等具体表现。不要上传配对文件、账号令牌或完整配置。

## 致谢与许可

基于 [LizardByte/Sunshine](https://github.com/LizardByte/Sunshine) 与 [LizardByte/libvirtualhid](https://github.com/LizardByte/libvirtualhid)。Sunshine 派生补丁遵循 GPL-3.0；这里涉及的 libvirtualhid 非驱动后端遵循 MIT，见 [许可说明](LICENSE.md)。没有包含或修改其专有 broker。

实现、调试和文档使用了 OpenAI Codex 辅助；硬件验收由真实用户完成。
