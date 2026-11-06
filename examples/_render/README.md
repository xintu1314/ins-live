# 新增参考案例制作说明

竖排字母示例已按反馈改为文字持续可见、逐行放大回落，无消散退场。

两个底图均使用内置 image_gen 生成，再用 Sharp + SVG 分层合成文字、磨砂 UI 和遮罩。没有将参考拼图直接变成生成案例。完整提示词见 [prompts.md](prompts.md)。

本渲染器仅复现这两个具体案例，包含为其底图校正的锚点；不是自动适配任意图片的通用渲染引擎。未将示例制作误称为用户认可。

在本目录安装 Node.js 依赖并执行：

```bash
npm install
node render.cjs keyframes
node render.cjs full
python3 ../../scripts/export_frames.py --frames-dir ../portrait-player/frames --pattern '%03d.png' --fps 20 --out-dir ../portrait-player --stem rerender
python3 ../../scripts/export_frames.py --frames-dir ../vertical-letters/frames --pattern '%03d.png' --fps 20 --out-dir ../vertical-letters --stem rerender
```

`source.png` 是生成底图；`keyframe.png` 为阅读阶段；`motion-check.jpg` 为 0、1.0、3.2、5.3 秒的连续抽帧。底图与关键帧已进行 390px 缩图检查；GIF / MP4 的 120 帧、6 秒与静音已由导出脚本检查。本次未声称已做完整实时播放检查。

渲染命令会重写示例目录内的 base / keyframe / 帧序列；如需保留旧渲染，先复制到独立目录。编码示例采用 rerender 文件名，避免覆盖仓库成品。参考的素材归属见仓库 ASSET-NOTICE.md。
