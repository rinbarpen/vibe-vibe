# 技术设计与引擎绑定 TDD
状态：draft；engine/version/host/targets：；设计 revision：

## 能力与架构
- adapter ID/版本来源、实际 Editor/SDK/插件、命令帮助记录：
- REQ-ID → 领域模块 → 引擎 Scene/World/Room/Entity/Event/Resource → owner：
- 初始化/销毁/场景切换、固定步长/渲染、事件/线程与状态机：
- 世界坐标轴/手性/单位、物理尺度、像素比例、UI 安全区、动作映射：
- 数据源/schema/随机种子、资源导入/GUID、缓存与生成物：
- 存档 schema/迁移/隔离样本；联网 authority/弱网/断线（若适用）：

## 性能与工具链
- 目标帧时 ms（例：60fps 对应约 16.67ms，需人确认）、内存 MB、下载包 MB、首屏与加载时间：
- CPU/GPU/物理/DrawCall/纹理/音频预算，测量设备、场景、样本数、p95/最大值阈值：
- source→export→import→build→runtime 链、版本锁定、可复建命令 cwd/env/stdout/stderr/exit：
- 缺失依赖、能力降级、not_run 项及恢复用例：

## 验收与回退
单测/场景测试/真实启动与输入/目标设备/真人试玩分层；每层 PASS 条件、证据路径与负责者。写明预期成功码，不默认所有引擎 exit=0。
修改前 commit/资源快照、存档样本、恢复命令和恢复后用例；不可逆迁移先决策。
