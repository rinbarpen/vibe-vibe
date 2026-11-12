# 执行、辅助脚本与交付

## 工作目录与版本

按项目实际复杂度使用 `source/`、`work/`、`exports/`、`textures/`、`previews/`、`qa/`。不要重组用户既有项目。修改前记录源文件 SHA256、软件版本、关键参数/插件；在新版本工作，外链资源一并备份。

保持 brief、当前原生文件、检查报告、返修问题和最新通过的机位连续；后续只处理未完成项。回退优先恢复上一版原生文件和匹配依赖，避免只回退网格却保留新贴图。

## 随附脚本及边界

| 脚本 | 执行环境 | 作用 | 不代表 |
|---|---|---|---|
| `blender_audit.py` | Blender `bpy` | 原始/viewport evaluated Mesh、边界/退化/UV层/图片/预算筛查 | 艺术合格、打印合格、最终渲染密度 |
| `blender_review.py` | Blender + Cycles CPU | 指定资产集合的六正交与两三分之四灰模/材质 PNG | 线框、定制近景、转台、已完成评审 |
| `check_delivery.py` | Python 3.11+ 标准库 | 清单结构、相对路径、文件/哈希、评审/再导入记录 | 真正打开原生文件、证明评审内容真实 |

Blender 脚本以 **4.5 LTS API** 为验证基线，不依赖付费插件。其他版本先用下述烟雾测试确认；不要把兼容基线当成当前最新版。

### 几何审计

以下 `SKILL` 指实际安装目录；`MODEL` 指当前工作副本。命令参数均用实际值替换。

```bash
SKILL=/absolute/path/to/3d-modeling-studio
MODEL=/absolute/path/to/model_v003.blend
QA=/absolute/path/to/qa
mkdir -p "$QA"
blender --background --factory-startup --disable-autoexec "$MODEL" \
  --python-exit-code 1 --python "$SKILL/scripts/blender_audit.py" -- \
  --collection ASSET --output "$QA/mesh-audit.json"
```

- 无 `--collection` 时扫描当前 view layer 的所有原始 Mesh，可能包含 cutter/地面；生产审计建议限定已明确的资产集合。
- 实体打印候选可加 `--closed-solid`；有 UV 要求加 `--require-uv`；项目设面数上限时加 `--max-triangles 100000`。数值只是命令例子，不是默认预算。
- 通过输出 `AUDIT PASS ...` 且退出 0；检测错误时保留 JSON，输出 `AUDIT FAIL ...` 并通过 `--python-exit-code 1` 以非零退出。不要省略该 Blender 参数后误判异常为成功。
- `status=pass` 仍可能含 warning。拓扑面积阈值 `--area-epsilon` 使用局部 Blender 单位平方；微小资产按尺度校准。
- `bounds_world` 是 Blender 场景坐标；实际物理长度还需对应 `unit_settings.scale_length`。边非流形检查不覆盖 bow-tie 顶点或自相交。
- 文件图片检查是 scene-wide 的保守筛查，可能涵盖未使用图片；UDIM、sequence、缓存和其他外部依赖标明另查。必要时清理交付副本未用数据后重测。
- evaluated 为 viewport depsgraph；最终 render levels、Geometry Nodes 实例、非 Mesh、毛发/体积另作宿主和渲染检查。脚本不会自动应用修改器或保存原生文件。

### 辅助检查图

```bash
blender --background --factory-startup --disable-autoexec "$MODEL" --threads 4 \
  --python-exit-code 1 --python "$SKILL/scripts/blender_review.py" -- \
  --collection ASSET --mode clay \
  --output-dir /absolute/path/to/previews/v003-clay
```

- 默认 768² / 32 samples / 8 views；`--resolution 256 --samples 8 --views front,back` 适合先测通路。
- `--mode material` 使用同一检查灯光下的原材质，不是原场景 beauty 或色彩匹配；另用项目原有渲染场景交最终表现图。
- 前 `-Y`、后 `+Y`、左 `-X`、右 `+X`、顶 `+Z`、底 `-Z`；前六张正交，后两张透视。使用包围球取景，长斜向部件也纳入画幅。
- 输出目录选新版本，脚本拒绝覆盖已存在的同名图片/清单。成功后 `review-manifest.json` 记录 PNG 哈希、视角、软件版本与 `visual_review_status=pending`。
- 脚本临时场景引用资产集合，不写回输入 `.blend`。保留原对象的 render visibility、材质和依赖；构建资产专用集合，移出灯光、地面、背景与 cutter。
- 约束/驱动/骨骼、跨集合依赖、collection instance、毛发/体积和 Geometry Nodes 实例可能需要专属渲染脚本；先检查依赖和代表性视图，勿把辅助图当复杂场景的完整支持。`--disable-autoexec` 禁用自动驱动脚本，确需可信驱动时单独核实配置后执行。
- 实际打开图片检查，再补真实线框、关键近景和用途专项证据。脚本成功只证明 PNG 已写出。

### 测试辅助工具

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s "$SKILL/tests" -p 'test_*.py' -v
blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
  --python "$SKILL/tests/blender_fixture.py" -- --output-dir /tmp/modeling-smoke
```

第二条只在新的临时目录生成几何/渲染测试夹具，不是高质量建模示例或用户资产生成器。生成后可对 `good.blend`、`open.blend`、`missing-texture.blend` 等运行上述审计，分别测试正例与反例；对 `render.blend` 运行辅助图。

## 交付清单格式

从 `assets/delivery.template.json` 复制到交付根目录的 `delivery.json`，填写真实软件/版本和相对路径。每个文件一条：

```json
{"path": "source/model.blend", "role": "source", "sha256": "64位SHA256十六进制字符串"}
```

`role` 可选 `source/exchange/preview/qa_report/review_record/roundtrip_record/texture/cache/script/other`。

最终包至少含原生源、交换件、预览、技术报告、视觉评审记录、重新导入记录这六种角色；有例外交付约定时调整项目方案，清楚说明不满足本工具的默认完整包规则，不伪造空文件应付检查。

- `technical_review` / `visual_review` / `roundtrip` 各含 `status` 和 `evidence`（对应清单内的路径）。技术报告、视觉评审记录和再导入记录分别使用对应角色。
- 状态统一 `pending/accepted/revise`。只有检查已执行且证据保存后填写 accepted。视觉问题 `issues` 至少给 `id/severity/status`，severity 为 `critical/major/minor`，status 为 `open/closed/accepted`；重大/阻断项必须关闭而非仅接受。
- 技术报告若为随附 Blender audit JSON，检查器要求 `pass`、源未变，且 source hash 对应交付的一个原生文件；网格或依赖修改后重跑。其他宿主报告的真实性/完整性由实际评审负责。
- `review_record` 应写具体视角、参考、分项观察、缺陷和决定；`roundtrip_record` 写实际应用/版本、导入文件 SHA256、参数、检查项、字面输出/截图与结论。
- 路径局限在交付根目录，禁止 `..` 和指向外部的符号链接；源/贴图均应真正打包或在约定布局下可访问。

```bash
python "$SKILL/scripts/check_delivery.py" /absolute/path/to/delivery/delivery.json \
  --stage draft
python "$SKILL/scripts/check_delivery.py" /absolute/path/to/delivery/delivery.json \
  --report /absolute/path/to/qa/delivery-check.json
```

`draft` 校验已列文件，允许暂缺角色/评审；`final` 默认要求六角色和三项 accepted 记录，无未关闭重大问题。退出 0=记录检查通过，2=记录检查失败。脚本不自动生成通过评语或改写 manifest。

## 导出与回退

1. 导出工作副本，记录格式/版本、单位、轴、应用变换、法线/切线、细分/实例/动画烘焙与材质处理。
2. 新建空场景或打开目标应用导入，核对尺寸/朝向、对象数量/层级、关键轮廓、材质贴图和动画/碰撞等约定项，保存证据。
3. 清单哈希在文件不再变动后生成。若后续返修，更新受影响文件、重做相关审计和再导入，并重算哈希。
4. 回退时关闭工作副本，恢复上一版本原生工程及相同版本依赖；重新打开确认基准。不要自动删除用户后续改过的资源。
