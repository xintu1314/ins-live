# 制作流程与项目记录

## 新任务与确认

每张新图用独立目录，内部保留 project.json。可执行：

```bash
python3 scripts/check_project.py init --source PHOTO --project-dir OUTPUT
python3 scripts/check_project.py check OUTPUT/project.json --stage proposals
python3 scripts/check_project.py check OUTPUT/project.json --stage selected
```

init 只读源文件并记录哈希，不生成图片，不覆盖旧项目。新附件不能继承旧选择；相同源图也可能是新任务，不凭哈希自动推断继续。“嗯嗯＋新图”不是确认。记录当前用户真实选择原话；脚本只能检查绑定关系，不能证明用户同意。

## 提案筛选

内部按空间容量、主体锚点、照片情绪、参考可用性和动作可实现性筛选整个库。方案必须有不同机制或空间关系；同一角色换姿势、同一 UI 换色不算。可以再次使用确实最适合的效果，但必须有新图依据，不固定同三项。

## 参考职责

| 职责 | 可决定 | 不能自动决定 |
| --- | --- | --- |
| 构图 | 尺寸、层级、留白、控件比例 | 新图的主体位置、人物身份、城市、文案 |
| 材质/字体 | 模糊/透明、线重、字体、圆角 | 把参考品牌或人物放进输出 |
| 动作 | 路径、相位、触发、接触、停留 | 从静图推断时序、把漂移擅改环绕 |
| 反例 | 识别已有失败 | 作为正向生成输入 |

每份选定媒体都要查看并写用途。不仅引用路径：播放器应观察卡片材质和比例；云朵小人应观察铅笔线、角色与接触点；地图观察平面与遮挡。

## 四项制作约束

1. 照片/锚点：保留区、不可遮挡区、归一化坐标、遮罩和前后顺序。
2. 视觉：主设计边界、参考职责、材质/字体/文字/颜色、允许变动范围。
3. 动作：主动作动词、关键状态、触发与时序、复位、首尾状态。
4. 分层：原图、UI、插画、文字、遮罩、共用布局参数和运动参数。

把资产/布局与时间函数分开。静帧和动画读取相同资产与布局定义，不在动作阶段另造相似角色或背景。复用组件，不复用上一张照片的全部锚点。

## 母版与检查阶段

关键帧先做，参考并排、390px缩图、必要局部放大都过关后才锁定底图/资产/布局/遮罩文件。母版不代表全图静止：按已选事件允许姿势和状态变化，身份与视觉语言稳定。更换创意回到提案，局部修复不额外询问审批。

之后先输出开场、最大变化、触发、结束四个试帧，确认动作明显与接触稳定，再完整渲染。正式导出后检查实际播放或带时间连续帧、尾首衔接、文件编码。

## 定向修复表

| 问题 | 修复层 | 保留 |
| --- | --- | --- |
| 太小/看不见 | 尺寸、对比、位移、停留 | 原图、正确机制和材质 |
| 灰卡像不透明贴纸 | 采样模糊、透明、边缘 | 布局和文字 |
| 字体/控件不像参考 | 字体层级、几何 | 照片和动作锚点 |
| 小人滑离杯沿 | 旋转坐标系、接触点 | 资产和配色 |
| 地图遮住鞋 | 透视层、遮罩 alpha | 内容与路线 |
| 数字提前变英文 | 共用线长进度 | 文案、布局、形状 |
| 字母错误环绕 | 独立轨迹与时序 | 字形和底图 |
| 尾首跳变 | 周期、透明度、重置段 | 正确的主动作 |

一次修复仍继承坏结构，就重建失败层，别反复叠编辑。检查记录不能虚构已查看、已同意或已通过。check_project.py 验证的是记录完整性与文件状态，不是审美。

## project.json 字段

init 创建 source、options、selection、checks。

- options：三个对象，各含 id、effect_id、placement、interaction、motion、palette、reason、references。references 用 skill 内相对路径。
- selection：option_id、source_sha256、user_message。必须对应本图实际选择。
- checks.reference：passed、reference_roles（path、role、inherit、exclude）、evidence（查看后的抽帧/记录文件）。
- checks.keyframe：passed、evidence、lock_files、observations。lock_files 包含实际共享的底图、图层或布局/遮罩。
- checks.motion：passed、evidence、observations（四个试帧及运动检查）。
- checks.delivery：passed、evidence、observations（导出与连续帧/首尾检查）。

关键帧通过后可用 check --stage keyframe --seal 锁定 lock_files 哈希。后续修改了通过项时应明确重新检查并重新 seal，不能悄悄修改再进入运动。证据路径为项目内文件；每个视觉阶段必须有观测记录，不把空路径或空列表当通过。
