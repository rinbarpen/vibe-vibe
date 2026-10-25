# Blender 本地适配器模板

这是一条可选的外部软件执行路径；不安装 Blender、不启动 MCP 服务，也不把模板当作已完成的模型。
`export_model.py` 导出**已有**场景中指定的网格，模型创作仍由建模执行 skill / 操作脚本完成。

## 使用

```bash
python .unity-game/scripts/dcc_cli.py doctor --blender /path/to/blender --output-dir Evidence/blender-doctor-001
python .unity-game/scripts/dcc_cli.py run --blender /path/to/blender \
  --project Art/robot.blend --script .unity-game/templates/Blender/export_model.py \
  --settings Art/robot-export.json --output-dir Evidence/robot-export-001

# 从零创作必须提供真正建模的脚本；factory-startup 的默认物体不代表完成设计。
python .unity-game/scripts/dcc_cli.py run --blender /path/to/blender --new --script Art/create_robot.py \
  --output-dir Evidence/robot-create-001
```

Blender 查找优先级：`--blender` → `BLENDER_BINARY` → PATH 中的 `blender`。
所有输出目录须全新。已有 `.blend` 先计算 SHA-256，再复制为 `source-copy.blend`，原文件不作为 Blender 打开目标。
同一源文件通过源路径锁串行执行；残留锁仅在核实对应进程结束后人工移除。
运行生成 `result.json`、版本探测与执行的 stdout/stderr、`job.json` 和冻结的 `operation.py`。
`doctor` 不带输出目录时仅打印结果，临时探测目录随后清理；需持久化证据时传入 `--output-dir`。

设置示例（物体名须来自实际场景）：

```json
{"objects": ["RobotBody", "RobotHead"], "render_preview": false}
```

省略 `objects` 表示导出全部网格。预览默认关闭；设 `render_preview: true` 时使用场景中**已配置**的相机、渲染器和灯光，不擅自重建构图。
模板保存 `model.blend`，导出 `model.fbx`，可选输出 `preview.png`，并写入拓扑、材质槽、纹理、世界包围盒、单位等审计数据。
拓扑统计是基础网格，不代表 modifier 求值后的最终三角面；最终预算以 Unity 导入后的实测为准。
骨骼、动作及特殊 shader 需独立脚本和专门验收；本模板只导出网格，不将其标记为已验证绑定模型。

## 自定义创作脚本契约

`run` 通过参数 `-- --job /absolute/job.json` 传入 JSON，字段为：

- `schema_version: 1`、`create_new: bool`、`source_copy: string | null`、`output_dir: string`、`settings: object`。
- 已有工程：`source_copy` 是已复制的 `.blend`；只修改工作副本。
- `--new`：从 factory-startup 环境开始，脚本明确清理默认物体、按规格创建自己的模型，保存新工程；不得将默认立方体作为设计成果。
- 脚本仅由用户/项目选定，本适配器不下载、不生成远程执行脚本；Blender 启动禁用自动执行 `.blend` 内嵌代码，但选定的 Python 脚本本身具备本地文件权限，应先审查。

完成后在输出目录原子写入 `asset-result.json`：

```json
{
  "status": "passed",
  "audit": {"mesh_count": 1, "triangles": 1200},
  "artifacts": [
    {"path": "model.blend", "role": "project", "sha256": "ACTUAL_SHA256"},
    {"path": "model.fbx", "role": "export", "sha256": "ACTUAL_SHA256"}
  ]
}
```

必须实际保存非空 `.blend` 和 `.fbx` / `.glb` / `.gltf`，使用文件真实哈希；审计数值来自软件 API。
helper 核对进程退出码、超时、JSON、非空文件、唯一且位于输出目录的路径、哈希及源文件未变。
该通过状态只代表本地执行/文件契约通过，**不是**模型艺术质量、Unity 导入、碰撞体、LOD、动画或设备性能验收通过。

## 依赖与验证边界

- `.blend` 副本中的相对纹理或链接库可能因迁移失效。执行前在源工程准备阶段打包依赖，或在自定义脚本中仅对副本重定位资源，审查纹理缺失清单。
- 导出模板对缺失引用纹理报错，不把缺纹理 FBX 当作完整交付；不自动下载或改写源工程依赖。
- Blender 未安装时返回 `not_run`，不产生模型成果。自动测试使用伪 Blender 验证 CLI 契约；真实 bpy、FBX 插件、预览渲染和 Unity 导入验收另行执行。
- 回退保留原始 `.blend`，不要将输出覆盖回源工程；废弃一次作业只需由用户移除该次新建输出目录。

API 依据：[Blender FBX 导出](https://docs.blender.org/api/current/bpy.ops.export_scene.html)、[工程保存](https://docs.blender.org/api/current/bpy.ops.wm.html)、[命令行参数](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)。
使用时按已安装 Blender 版本核对文档和导出插件支持。
