---
name: excalidraw
description: Archived legacy reference. excalidraw is no longer supported or routed by Omnidraw.
---

# Excalidraw

> Archived: this legacy reference is retained for history only and is not a supported Omnidraw route.


Hand-drawn / sketch style diagrams with rough.js aesthetic. Perfect for whiteboard-style architecture discussions, wireframes, and quick mockups.

## When to Use

- Hand-drawn / sketch style diagrams
- Whiteboard-style architecture discussions
- Quick wireframes and mockups
- Collaborative diagramming with live rooms
- When you want a "thinking on paper" aesthetic

**Not for**: production diagrams (use [drawio](../drawio/SKILL.md)), UML (use [plantuml](../plantuml/SKILL.md)).

## Quick Start

### URL Scheme
Generate a diagram description and open it:
```
https://excalidraw.com/#json=[URL-encoded JSON]
```

### Online Editor
Go to https://excalidraw.com and draw directly.

### npm Library
```bash
npx create-excalidraw-file
```

## Key Features

- Hand-drawn aesthetic (rough.js)
- Infinite canvas with zoom/pan
- Real-time collaboration via rooms
- Export: PNG, SVG, Excalidraw JSON
- Library of community shapes
- Dark/light mode

## Programmatic Elements

```javascript
{
  type: "rectangle",
  x: 100, y: 100,
  width: 200, height: 100,
  strokeColor: "#000000",
  backgroundColor: "#ced4da",
  roughness: 1,
  opacity: 100
}
```

Shapes: `rectangle`, `ellipse`, `diamond`, `arrow`, `line`, `text`, `image`, `freedraw`

## Templates

```
Architecture sketch:
  Create an Excalidraw whiteboard sketch: [system] architecture. Hand-drawn rectangles for [services], arrows for data flow. Include notes and annotations.

Wireframe:
  Create an Excalidraw wireframe for [screen/page]: header, sidebar, main content area, footer. Rough rectangles, placeholder text, simple icons.

Flow:
  Create an Excalidraw sketch: [process flow] from [start] to [end]. Hand-drawn shapes, curved arrows, sticky-note style annotations.
```
