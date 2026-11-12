# 研究发现

- 仓库无 .codegraph/，无需索引查询。初始 git status 干净；mine/ 无额外 AGENTS.md。
- 可用 Python 3.12、uv、vibe；PATH 暂无 blender。
- 已读取 skill-creator、UI metadata 和 planning-with-files-zh。将详细内容按软件/资产/质量分层。
- 官方检索证实 Blender 烘焙、ZBrush ZRemesher、C4D Volume Builder、Houdini Remesh 的适用场景。
- Maya Quad Draw 是手动拓扑路线；Maya 2026 Flow Retopology 文档描述云处理，因此不把它作为默认本地依赖。
- Rhino QuadRemesh 目标四边面数并非精确数量；SubD 显示/渲染网格密度规则不同。
- Fusion Python/C++ 脚本在宿主 Scripts and Add-ins 环境运行，普通 Python 不是 Fusion 宿主。

## 官方来源（待将相关条目整理进 Skill）
- https://docs.blender.org/manual/en/latest/
- https://help.maxon.net/zbr/en-us/Content/html/reference-guide/tool/polymesh/geometry/zremesher/zremesher.html
- https://help.maxon.net/c4d/en-us/Content/html/OVOLUMEBUILDER.html
- https://www.sidefx.com/docs/houdini/nodes/sop/remesh.html
- https://help.autodesk.com/cloudhelp/2024/ENU/Maya-Modeling/files/GUID-03933C1F-1BA7-4E7E-AAB5-31FB0E6A77B2.htm
- https://docs.mcneel.com/rhino/8mac/help/en-us/commands/quadremesh.htm
- https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/WritingDebugging_UM.htm

- 资料抓取：web 对 Blender 4.5 文档返回 402，shell 直连官方 API 页面成功；通过官方 release 索引获得 4.5.9 Linux 包，正在独立临时目录下载并验证 SHA256。
- 已创建 Skill 骨架：mine/3d-modeling-studio。Blender 4.5 为脚本验证基线，不称为当前最新版。
- 执行 vibe 后出现两处 tracked __pycache__ 变动；另有并发新增的 tests/test_ui_usability_manifest.py，后续保持独立、不触碰此测试。
- 质量需明确：自动审计只覆盖几何/依赖等可计算项；审美、变形、自相交/壁厚/CAD连续性需专项证据。

- 首轮 Blender 实测：closed-solid + require-uv 的细分正例通过；8 张 PNG 写出成功且原始 .blend 哈希不变。
- 实际查看前视、背三分之四、底视后发现灰模曝光偏亮；已把辅助灯能量从 250*r² 降至 35*r²，重渲染对照，不把“出图成功”等同于图像可用。
- 补强了交付检查器对损坏 audit 哈希字段的处理；空控制笼但 evaluated 已生成网格仅提示 warning，避免误杀程序化路线。

## 最终结果
- Skill 路径：mine/3d-modeling-studio，16 个文件；7 份专项参考、2 个 JSON 模板、3 个执行脚本、2 个测试文件、入口和 UI 元数据。
- 最终灰模能量 70*r²，8 视图实际查看通过烟雾图可读性检查；不对技术夹具进行优秀作品评分。
- .vibe-tool/backups/3d-modeling-studio-20261108/ 保存 patch、verification.json、rollback.py、created-files.json、基准清单、宿主输出与可分发 ZIP。
- 商业软件覆盖的是可执行工作流/运行方式说明；当前宿主实测范围明确是 Blender 4.5.9 LTS。
