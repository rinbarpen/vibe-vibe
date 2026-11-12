# Draw.io References

## MCP Tools Reference

| Tool | Parameters | Returns | Description |
|------|-----------|---------|-------------|
| `start_session` | `port` (optional) | Session info | Opens browser preview |
| `create_new_diagram` | `xml` (string) | Diagram ID | Creates diagram from mxGraph XML |
| `edit_diagram` | `operations` (array) | Updated diagram | Edit by ID-based operations |
| `get_diagram` | — | Current XML string | Retrieves full diagram XML |
| `export_diagram` | `path` (string) | File path | Saves `.drawio` file |

## Edit Operations

```json
{
  "operations": [
    {"action": "add", "type": "vertex", "style": "...", "value": "Label", "x": 100, "y": 100, "width": 120, "height": 60},
    {"action": "add", "type": "edge", "style": "...", "value": "Label", "source": "cell-0", "target": "cell-1"},
    {"action": "update", "id": "cell-0", "style": "...", "value": "New Label"},
    {"action": "delete", "id": "cell-0"}
  ]
}
```

## Diagram Type Guidance

| Type | Layout | Key Shapes | Best Practice |
|------|--------|------------|---------------|
| Flowchart | TD/LR | Rounded rect, diamond, circle | Orthogonal connectors; decision nodes always diamond |
| Architecture | TD (layered) | Rounded rect, cylinder (DB), cloud | Subgraphs per layer; consistent sizing |
| Network | Free | Router, switch, firewall icons | Subnets as containers; bandwidth labels |
| Cloud | TD (layered) | Cloud service icons | VPC boundary; AZ grouping |
| Sequence | TD | Lifeline rect, activation bars | Message labels on arrows |
| UML | TD/LR | Class rect, interface circle | UML notation consistent |
| ERD | Free | Entity rect, relationship diamond | Crow's foot via connector labels |
| Patent | TD/LR | Rounded rect, diamond | B&W, 15px, orthogonal, no fill colors |
| Academic | TD/LR | Rounded rect, cylinder | Grayscale, LaTeX math, 300 DPI |

## Key Constraints

- **Patent figures**: 15px font, B&W, no grayscale, caption outside
- **IEEE papers**: Grayscale, EPS/PDF, LaTeX, 300 DPI
- **ACM**: PDF/PNG, LaTeX for math
- **Presentations**: 18pt+ font, high contrast, 16:9 ratio
- **Chinese journals**: 宋体, 中英双语标注, 300 DPI
