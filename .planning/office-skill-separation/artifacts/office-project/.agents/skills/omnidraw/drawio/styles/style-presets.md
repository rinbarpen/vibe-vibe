# Draw.io Style Presets

Copy-paste style strings. Semicolon-separated `key=value` pairs.

## Color Palette

```
Primary fill:     #dae8fc    Primary stroke:     #6c8ebf
Success fill:     #d5e8d4    Success stroke:     #82b366
Warning fill:     #fff2cc    Warning stroke:     #d6b656
Danger fill:      #f8cecc    Danger stroke:      #b85450
Neutral fill:     #f5f5f5    Neutral stroke:     #666666
Dark fill:        #1a1a2e    Dark stroke:        #333366
```

## Node Presets

### Primary (Service/Component)
```
rounded=1;html=1;whiteSpace=wrap;align=left;verticalAlign=middle;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=15;fontColor=#000000;spacingLeft=10;spacingRight=10;spacingTop=6;spacingBottom=6
```

### Success (Data/Result/DB)
```
rounded=1;html=1;whiteSpace=wrap;align=left;verticalAlign=middle;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=15;fontColor=#000000;spacingLeft=10;spacingRight=10;spacingTop=6;spacingBottom=6
```

### Warning (Decision/Condition)
```
rhombus;html=1;whiteSpace=wrap;align=center;verticalAlign=middle;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=15;fontColor=#000000
```

### Danger (Error/Failure)
```
rounded=1;html=1;whiteSpace=wrap;align=left;verticalAlign=middle;fillColor=#f8cecc;strokeColor=#b85450;fontSize=15;fontColor=#000000
```

### Container (Subgraph/Layer)
```
rounded=1;html=1;whiteSpace=wrap;align=left;verticalAlign=top;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontColor=#333333;dashed=1;dashPattern=8 4
```

### Database (Cylinder)
```
shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;fontColor=#000000
```

### Cloud
```
ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#999999;fontSize=14;fontColor=#333333
```

### Start/End (Terminal)
```
ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=15;fontColor=#000000
```

## Edge Presets

### Standard Arrow
```
edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;strokeColor=#666666;strokeWidth=1;fontSize=12;fontColor=#333333
```

### Dashed Arrow (Data Flow)
```
edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;strokeColor=#999999;strokeWidth=1;dashed=1;dashPattern=4 4;fontSize=12
```

### Bold Arrow (Main Flow)
```
edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;strokeColor=#333333;strokeWidth=2;fontSize=13;fontColor=#000000;fontStyle=1
```

### Bidirectional
```
edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;startArrow=classic;strokeColor=#666666;strokeWidth=1
```

## Theme Presets

### Professional (Blue/Gray)
Nodes: Primary (#dae8fc / #6c8ebf), Neutral (#f5f5f5 / #666666)
Edges: Standard Arrow (#666666, orthogonal)
Font: 15px, #000000

### Patent (B&W)
Nodes: White (#ffffff / #000000), no fill colors
Edges: Black (#000000, orthogonal, straight)
Font: 15px, #000000, Chinese-capable
No grayscale. No shading. Pure line art.

### Academic (Grayscale)
Nodes: Light gray fill (#f0f0f0 / #666666)
Edges: Gray (#666666)
Font: 14px, serif-capable, LaTeX math support

### Dark Mode
Nodes: Dark fill (#1a1a2e / #333366), Light text (#e0e0e0)
Edges: #555588
Font: 15px, #e0e0e0

### Cloud Native
Nodes: Blue primary (#dae8fc / #6c8ebf), Green data (#d5e8d4 / #82b366)
Edges: Standard Arrow, dashed for async/data
Font: 14px
