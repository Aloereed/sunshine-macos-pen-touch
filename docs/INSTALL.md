# 在 Mac 上构建和试用

本指南只改新建的源码目录和测试应用，不要求修改 EFI、SIP、NVRAM，也不需要安装数位板内核驱动。

已实测的是 Intel macOS 上的补丁实现。下面的 Homebrew 步骤是依据固定版本上游构建文件整理的通用路线；原实测构建使用隔离依赖前缀，并非全新 Homebrew 环境。Apple Silicon 和其他 macOS 版本尚未实机验证。

## 1. 准备工具

需要 Git、Python 3.9+、较新的 Xcode Command Line Tools（原实测 Apple clang 21）、CMake、Ninja、Node/npm、OpenSSL、Opus、miniupnpc。已有的工具无需重复安装。

```sh
xcode-select -p
brew install cmake ninja node openssl@3 opus miniupnpc pkgconf
```

这里关闭托盘 UI，管理仍使用 Sunshine 网页。CMake 会准备其他上游依赖和对应 build-deps 的 FFmpeg，需要能访问 GitHub/npm。也可参考[固定基线的上游构建文档](https://github.com/LizardByte/Sunshine/blob/63d35f702ee9e362e43263742981836ec0710384/docs/building.md)。

## 2. 下载补丁和固定源码

以下命令假设当前目录用于存放新建的工作目录；如果同名目录已存在，请换一个空目录，不要覆盖已有工作。

```sh
git clone https://github.com/Aloereed/sunshine-macos-pen-touch.git
git clone --no-checkout https://github.com/LizardByte/Sunshine.git Sunshine-pen-touch
git -C Sunshine-pen-touch checkout --detach 63d35f702ee9e362e43263742981836ec0710384
git -C Sunshine-pen-touch submodule update --init --recursive

python3 sunshine-macos-pen-touch/scripts/apply-patches.py Sunshine-pen-touch --check-only
python3 sunshine-macos-pen-touch/scripts/apply-patches.py Sunshine-pen-touch
```

脚本只应用 Sunshine 集成与其固定 libvirtualhid 的回移补丁。不需要额外应用 `libvirtualhid-macos-pen.patch`；那个补丁用于单独开发较新的库版本。

## 3. 构建程序、网页和测试

在刚才的父目录执行。保留完整工作目录，先不要安装到系统目录。

```sh
export BRANCH=macos-pen-touch
export BUILD_VERSION=2026.914.233613
export COMMIT=63d35f702ee9e362e43263742981836ec0710384
export PKG_CONFIG_PATH="$(brew --prefix opus)/lib/pkgconfig:$(brew --prefix openssl@3)/lib/pkgconfig:${PKG_CONFIG_PATH:-}"

cmake -S Sunshine-pen-touch -B Sunshine-pen-touch/cmake-build-pen -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_DOCS=OFF -DBUILD_TESTS=ON \
  -DSUNSHINE_ENABLE_TRAY=OFF \
  -DLIBVIRTUALHID_BUILD_MACOS_BROKER=OFF \
  -DOPENSSL_ROOT_DIR="$(brew --prefix openssl@3)" \
  -DCMAKE_PREFIX_PATH="$(brew --prefix)" \
  -DSUNSHINE_PUBLISHER_NAME='Community pen and touch patch'

# 先生成网页，确保应用打包时能带上资源。
cmake --build Sunshine-pen-touch/cmake-build-pen --target web-ui
cmake --build Sunshine-pen-touch/cmake-build-pen --target sunshine test_sunshine -j 4
Sunshine-pen-touch/cmake-build-pen/tests/test_sunshine \
  --gtest_filter='VirtualHidDeviceTest.*:InputGamepadSessionTest.*'

# 重建网页后也可重复此复制，避免旧资源留在 .app 中。
ditto Sunshine-pen-touch/cmake-build-pen/assets \
  Sunshine-pen-touch/cmake-build-pen/Sunshine.app/Contents/Resources/assets
```

如果 CMake 找不到 SDK 的 libcurl，可以显式添加 Homebrew 的 curl 开发文件后重新配置：

```sh
brew install curl
export PKG_CONFIG_PATH="$(brew --prefix curl)/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
# 重新执行上面的 cmake 配置命令，再继续构建。
```

不要通过修改 `/usr/include` 或系统 OpenSSL 路径解决依赖问题。构建失败时保留第一个实际报错；本仓库不捆绑整个依赖工具链。

## 4. 创建独立测试应用

```sh
python3 sunshine-macos-pen-touch/scripts/stage-app.py \
  Sunshine-pen-touch/cmake-build-pen/Sunshine.app \
  'Sunshine Pen Touch.app'
```

该脚本使用 `ditto` 复制完整应用，设置独立 bundle ID，再进行 ad-hoc 签名和签名校验。目标已存在会拒绝覆盖；没有开发者公证，不代表 Apple 信任认证。此 Homebrew 构建可能动态依赖本机库，不能直接把应用拷给其他电脑当通用安装包。

把新应用移动到 `/Applications` 或 `~/Applications`，选定最终位置后再授予权限。保留原版 Sunshine 应用及原来的启动方式。

## 5. 授权并试运行

1. 在 **系统设置 → 隐私与安全性 → 辅助功能** 添加并启用新应用。
2. 在 **屏幕与系统音频录制** 添加并启用同一个新应用。旧 Sunshine 的权限不保证能沿用；重新编译签名后也可能需要重新授权。
3. 保留现场键鼠或其他远程入口，通过你原本的方式停止旧 Sunshine。若有自动拉起服务，先停止它的服务任务；不要让两个实例争用同一端口。本文不假设你使用哪种 LaunchAgent/Homebrew 配置。
4. 从终端启动测试版以便看到错误：

```sh
'/Applications/Sunshine Pen Touch.app/Contents/MacOS/Sunshine'
```

如放在其他位置，修改命令中的路径。若原版通过参数指定配置文件，请沿用相同参数；不要在反馈中贴出配置内的密码或密钥。新实例通常沿用同一用户下的 Sunshine 配置与配对信息；操作前自行保留原配置备份。

5. Sunshine 的 `native_pen_touch` 不应被禁用。重新连接支持笔协议的客户端，让它重新获取能力。
6. 打开 Krita，选压力控制大小的笔刷，轻重画线；再用手指点击菜单、拖动窗口标题栏。

正常结果应同时包含压感和单指 UI 操作。普通鼠标事件也能画线，不能仅凭“画得出来”判定压感成功。测试通过后，再按你现有的服务管理方式把启动路径改到新应用；本仓库不自动改变开机启动。

## 6. 回退

终端前台运行时按 Ctrl+C 停止测试版，再用原来的方式启动官方 Sunshine。若后来调整过开机启动路径，把它改回原应用。无需重启 Mac或修改系统安全配置。不要删除原有配对/账号数据来回退输入补丁。

## 常见问题

- **有画面、没有输入**：核对辅助功能授权是否属于当前签名和路径的测试应用。
- **黑屏/无法捕获**：核对录屏权限与捕获显示器，不要先改输入补丁。
- **能画线但无压感**：先确认绘画笔刷启用压力控制，并确认输入是数位笔事件而非鼠标模拟。
- **触点落在另一个显示器**：单指鼠标映射目前只支持主显示器；先把捕获屏幕设为主屏。
- **只有可执行程序、没有网页**：必须构建 `web-ui` 并将 `cmake-build-pen/assets` 放入应用资源目录。
- **端口占用、退出后又自动启动**：检查原来的 Sunshine 服务管理方式，确保只运行一个实例。
