# Draw.io Prompt Templates

Copy-paste prompts organized by diagram type.

---

## Flowchart

### Basic Process
```
Create a flowchart (graph TD) for [process name]:
[step1] → [step2] → {decision diamond: [question]} → [path A] / [path B].
Both paths converge at [final step]. Use subgraph "Pre-processing" for steps 1-2.
Style: start node green (#d5e8d4), decision yellow (#fff2cc), end node blue (#dae8fc).
Orthogonal connectors. Export as [format].
```

### Decision Tree
```
Draw a decision tree: [root question] → [branch1]/[branch2]/[branch3].
Each branch has 2-3 levels of sub-decisions. Diamond shapes for all decision nodes.
Leaf nodes are rounded rectangles with final outcomes.
Left-to-right layout (LR). Professional blue palette.
```

---

## Architecture

### System Architecture
```
Draw a system architecture diagram for [system name]:
Layers (top to bottom): [Client/Presentation] → [API Gateway] → [Service Layer] → [Data Layer].
Components: [list each with short description].
Containers/subgraphs for each layer. Data flow arrows with labels.
Professional style, 3-4 color palette. Export .drawio + PNG.
```

### Microservices
```
Draw a microservices architecture:
API Gateway → [Service A], [Service B], [Service C].
Each service with own DB. Shared Redis cache. Message queue (RabbitMQ/Kafka).
Service discovery (Consul/Eureka). Config server. Monitoring (Prometheus/Grafana).
Layered layout. Standard blue/green/gray palette.
```

### Cloud (AWS)
```
Generate AWS architecture: [region/AZs].
[Service list with short descriptions]. Use official AWS icons.
Group by VPC. Show public/private subnet boundaries.
Security groups, IAM roles where relevant. Data flow arrows.
```

---

## Network

### Network Topology
```
Draw a network topology diagram:
[Router/Firewall] → [Core Switch] → [Access Switches] → [Endpoints].
VLANs: [VLAN10], [VLAN20], [VLAN30].
WAN link, DMZ. Use standard network icons.
Orthogonal connectors. Label bandwidths on links.
```

---

## Sequence

### API Sequence
```
Create a sequence diagram:
Participants: Client, API Gateway, [Service], Database.
1. Client → API Gateway: [request]
2. API Gateway → [Service]: [transformed request]
3. [Service] → Database: [query]
4. Database → [Service]: [result]
5. [Service] → API Gateway: [response]
6. API Gateway → Client: [final response]
Add activation bars. Add alt/else for error path.
```

---

## Patent (专利)

### Structure Diagram
```
Draw a Chinese patent structure diagram (结构示意图):
System: [name]. Modules: [A, B, C, D] with clear boundaries.
A–H format:
A. Structure Diagram
B. [title]
C. [nodes with labels and types]
D. [edges with descriptions]
E. Top-down layout
F. Patent style — 15px font, black text, B&W only, no grayscale
G. Export PNG 300dpi
H. Caption outside image: 图N [title]结构示意图
Use orthogonal connectors with right-angle routing.
```

### Method Flowchart
```
Draw a Chinese patent method flowchart (方法流程图):
Steps: 开始 → [step1] → [step2] → {判断: [condition]} → [step3a] / [step3b] → 结束.
Rounded rect for process steps, diamond for decision, circle for start/end.
15px font, black text, Chinese labels. B&W only. Orthogonal lines.
Caption: 图N [title]方法流程图.
```

---

## Academic Paper

### IEEE Architecture
```
Draw an IEEE-compliant architecture diagram:
Grayscale only (no color). LaTeX math with $$ delimiters.
Sans-serif font, consistent sizing. Clear component boundaries.
300 DPI minimum. Export as EPS/PDF vector.
Caption style: Fig. N. [Title].
Standard IEEE double-column width constraints.
```

### Pipeline Figure
```
Draw a pipeline/training flow figure for [conference — CVPR/NeurIPS/ICML]:
Input → [Stage 1] → [Stage 2] → [Stage 3] → Output.
Show data tensor dimensions at each stage.
Grayscale with LaTeX math. Export PDF vector format.
```

---

## Quick Templates (Chinese)

### 系统架构图 (中文期刊)
```
绘制用于[期刊名]的系统架构图:
[N]个主要模块, 宋体10-12pt标注。中英双语图注。
灰度图, 300 DPI。导出 EPS/PDF。图题: 图N [系统名]系统架构图。
```

### 技术路线图 (国自然)
```
绘制国自然技术路线图:
[阶段1] → [阶段2] → [阶段3] → [阶段4]。
每个阶段标注: 研究内容, 关键方法, 预期产出。
学术风格, 蓝灰配色, 宋体标题。导出 PDF。
```
