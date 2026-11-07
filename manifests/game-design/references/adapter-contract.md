# 引擎适配协议

## 一份设计，多种工程映射

GDD 描述玩家体验和行为，不写某引擎 API 为前提。TDD 将 REQ-ID 映射到所选引擎的实体/场景、脚本/数据、资源与工具，并明确测试/导出证据。转换引擎是迁移决策，不是替换引擎名。

每个 engines.json 条目必须包含：稳定 ID/name/category、fit、detection、version、scene、code、assets、space、input、save_network、tests、build、pitfalls、sources、support、runtime_validation。`check-catalog` 检查完整性；`render-adapters` 从该数据生成可读指南，避免目录与文档双份手工维护。

## 必须绑定的项目能力

| 适配面 | 项目需明确的事实/证据 |
|---|---|
| 识别/版本 | 实际引擎/版本、项目位置、OS、锁文件、依赖、SDK、工具路径；检测命中仅为线索 |
| 实体/生命周期 | GDD 对象、状态和关卡在 Scene/World/Node/Room/Event/ECS 的归属，初始化/销毁/切场景规则 |
| 脚本/数据 | 语言/运行时、纯领域边界、数值源/生成物、schema 与迁移、随机种子和固定模拟步长 |
| 资源 | 源/导出/缓存目录、GUID/UID/ID、模型/动画/材质/贴图/音频/字体、许可、压缩和异步加载 |
| 坐标/输入 | 轴向、手性、单位、像素密度、物理尺度、相机、UI 安全区、键鼠/手柄/触控动作表 |
| 存档/联网 | 写入路径、旧档样本和 schema、断电/重试；联网需要 authority、同步、弱网和测试数据隔离 |
| 测试 | 静态/单测/场景测试/构建/真实游玩/目标设备/真人反馈分别记录，缺工具为 not_run |
| 发布 | 本机工具/许可证/平台资格、真实命令、预期退出码、日志、产物路径/hash、签名、发布门与回退 |

## 按需加载与能力降级

- 只读所选 adapter；Web renderer 与完整引擎分开。没有场景、物理、存档、编辑器的框架，应在 TDD 中显式补设计，不能借用 Unity 概念宣称已具备。
- CLI/MCP 已连接且适用时优先程序化路径；只能 GUI 的编辑器使用项目允许的 GUI 工具/人工步骤，记录操作输入输出。不臆造每个引擎通用的 `--headless --test --export`。
- 构建模板中的变量全部解析、核验 `--help` 与工具版本后再执行；写清 host shell、cwd、环境和引擎特定退出码。Cocos Creator 3.8 成功码 36 是重要反例。
- 本机没有某 Editor/设备时可完成设计映射与纯数据测试；运行时保持 not_run，并说明所缺依赖和恢复用例。文档/目录检查不能替代引擎启动、资产导入和实际游戏操作。
- VR/XR、主机、小游戏、多人、mod 和 live-ops 是横切能力，不因选某引擎而自动通过；平台规则与 SDK/许可按项目和日期核验。

## 添加新引擎

1. 以官方对应版本资料填写完整条目，登记限制与可复现测试入口，不宣称未运行结果。
2. 识别规则应依赖特征签名，避免任意 package.json/Cargo.toml/project.json；未知/冲突不自动选择。
3. 为独立规则创建正例、误判反例与多引擎冲突用例；实际引擎测试分开记录。
4. 运行 check-catalog、render-adapters、render-adapters --check 及模板测试；原流程有变化时同步更新 workflow 源与 SVG。

Unity 深化适配复用仓库的 unity-game 与 unity-game-development，不复制其 skill-map.json 或 renderer。新 manifest 的 workflow 表达跨引擎流程，与 Unity 原工作流分别维护。
