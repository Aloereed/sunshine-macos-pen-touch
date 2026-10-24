# 开发者说明

普通试用走 [INSTALL.md](INSTALL.md)，只需要 Sunshine 和其固定依赖的两个运行时补丁。

若要独立开发或审阅较新的 libvirtualhid 笔后端，可在一个独立目录中操作：

```sh
git clone --no-checkout https://github.com/LizardByte/libvirtualhid.git libvirtualhid-pen-review
git -C libvirtualhid-pen-review checkout --detach 45c9b4db05779d18224a751e33cb8dfea78201bb
git -C libvirtualhid-pen-review submodule update --init --recursive
cd libvirtualhid-pen-review
git apply --check ../sunshine-macos-pen-touch/patches/libvirtualhid-macos-pen.patch
git apply ../sunshine-macos-pen-touch/patches/libvirtualhid-macos-pen.patch
cmake -S . -B cmake-build-pen -G Ninja \
  -DBUILD_DOCS=OFF -DBUILD_EXAMPLES=OFF -DBUILD_TESTS=ON \
  -DLIBVIRTUALHID_BUILD_TOOLS=OFF -DLIBVIRTUALHID_BUILD_MACOS_BROKER=OFF \
  -DLIBVIRTUALHID_ENABLE_PACKAGING=OFF
cmake --build cmake-build-pen -j 4
cmake-build-pen/tests/test_libvirtualhid
```

这个较新 API 的库补丁不能直接替代 Sunshine 旧固定依赖的回移补丁。回移与完整库补丁有不同基线，修改 API 后必须重新适配和测试。

## 后端约定

- 使用 CoreGraphics 事件注入，不声明物理数位板设备。
- 笔 viewport 是屏幕逻辑点，不是 Retina backing pixels。
- 保留 proximity、笔/橡皮擦身份、压力、倾斜与两枚侧键；取消/退出清理状态。
- tablet-point 移动事件保留较高压力精度，mouse down/up 子类型路径精度较低，不能宣称全程 16 位压感。
- 单指回退使用每客户端鼠标实例；当前映射为主显示器，非完整触屏设备。

本仓库的辅助脚本可以运行 `python3 -m unittest discover -s tests -v` 验证。它们不代替上游 C++ 测试与真实设备验收。
