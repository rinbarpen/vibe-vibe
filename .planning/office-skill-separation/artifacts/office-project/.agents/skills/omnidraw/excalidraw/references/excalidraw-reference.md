# Excalidraw Reference

## Quick Start

**Web**: https://excalidraw.com
**npm**: `npm install @excalidraw/excalidraw` or `npx create-excalidraw-file`
**VSCode**: Excalidraw extension

## Element Types

| Type | Fields | Use |
|------|--------|-----|
| `rectangle` | x, y, width, height, roundness | Boxes, containers |
| `ellipse` | x, y, width, height | Circles, ovals |
| `diamond` | x, y, width, height | Decision nodes |
| `arrow` | x, y, width, height, points | Connectors |
| `line` | x, y, width, height, points | Lines, dividers |
| `text` | x, y, text, fontSize, fontFamily | Labels, notes |
| `image` | x, y, fileId | Embedded images |
| `freedraw` | points | Freehand drawing |

## Programmatic API (JSON)

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "type": "rectangle",
      "version": 1,
      "id": "rect-1",
      "x": 100, "y": 100,
      "width": 200, "height": 80,
      "angle": 0,
      "strokeColor": "#000000",
      "backgroundColor": "#ced4da",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "roundness": { "type": 3 },
      "groupIds": [],
      "boundElements": [],
      "isDeleted": false,
      "locked": false
    }
  ],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": 20
  }
}
```

## Style Properties

| Property | Values | Effect |
|----------|--------|--------|
| `roughness` | 0-2 | 0 = perfect, 1 = sketchy, 2 = very rough |
| `strokeStyle` | `solid`, `dashed`, `dotted` | Line style |
| `fillStyle` | `solid`, `hachure`, `cross-hatch`, `zigzag`, `dashed`, `solid` | Fill pattern |
| `opacity` | 0-100 | Transparency |
| `strokeWidth` | 1-4 | Line thickness |
| `roundness` | `{ "type": 1 }`, `{ "type": 2 }`, `{ "type": 3 }` | Corner radius (sharp/medium/rounded) |

## URL Scheme

```
https://excalidraw.com/#json=[URL-encoded JSON]
https://excalidraw.com/#room=[room-id],[encryption-key]  (collaboration)
```

## Export Formats

| Format | How |
|--------|-----|
| PNG | File → Export → PNG (scale 1x/2x) |
| SVG | File → Export → SVG |
| Excalidraw JSON | File → Save / Export |
| Clipboard | Select → Ctrl+C → paste as PNG |

## Libraries (Community Shapes)

In Excalidraw: click "Library" → "Browse libraries" → add shapes.
Or create custom library via JSON export.

## Best Practices

- Use `roughness: 1` for the classic Excalidraw hand-drawn look
- Group related elements for easy repositioning
- Use the grid (snap to grid) for alignment
- Export at 2x scale for retina displays
- Share via room link for real-time collaboration
- Dark mode: toggle in menu or set `viewBackgroundColor: "#121212"`

## Excalidraw vs Other Tools

| Need | Excalidraw | Better Alternative |
|------|-----------|-------------------|
| Hand-drawn aesthetic | ✓ | — |
| Real-time collaboration | ✓ | — |
| Production diagrams | — | [drawio](../../drawio/SKILL.md) |
| UML | — | [plantuml](../../plantuml/SKILL.md) |
| Data charts | — | [matplotlib](../../matplotlib/SKILL.md) |
| Quick markdown embedding | — | [mermaid](../../mermaid/SKILL.md) |
