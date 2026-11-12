# Mermaid Theme / Style Presets

Mermaid supports theming via `%%{init: {...}}%%` directives at the top of the diagram.

## Built-in Themes

```
%%{init: {'theme': 'default'}}%%
%%{init: {'theme': 'forest'}}%%
%%{init: {'theme': 'dark'}}%%
%%{init: {'theme': 'neutral'}}%%
%%{init: {'theme': 'base'}}%%   — matches GitHub rendering
```

## Custom Theme

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#dae8fc',
    'primaryTextColor': '#000000',
    'primaryBorderColor': '#6c8ebf',
    'lineColor': '#666666',
    'secondaryColor': '#d5e8d4',
    'tertiaryColor': '#fff2cc',
    'fontSize': '14px',
    'fontFamily': 'system-ui, sans-serif'
  }
}}%%
```

## Theme Variable Reference

| Variable | Applies To |
|----------|-----------|
| `primaryColor` | Main node fill |
| `primaryTextColor` | Main node text |
| `primaryBorderColor` | Main node border |
| `secondaryColor` | Secondary fills (subgraphs, notes) |
| `tertiaryColor` | Tertiary fills (alt blocks) |
| `lineColor` | All edges, connectors |
| `textColor` | Labels, annotations |
| `fontSize` | Global font size |
| `fontFamily` | Font stack |

## Preset Themes

### Professional Blue
```
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#dae8fc', 'primaryBorderColor': '#6c8ebf',
  'primaryTextColor': '#1a1a2e', 'lineColor': '#6c8ebf',
  'secondaryColor': '#f0f4ff', 'tertiaryColor': '#e8f0fe',
  'fontSize': '14px'
}}}%%
```

### Warm Earth
```
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#f5e6d3', 'primaryBorderColor': '#c4a882',
  'primaryTextColor': '#3d2b1f', 'lineColor': '#c4a882',
  'secondaryColor': '#faf3e6', 'tertiaryColor': '#f0e4d0',
  'fontSize': '14px'
}}}%%
```

### Dark Mode
```
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#2d2d44', 'primaryBorderColor': '#5a5a8a',
  'primaryTextColor': '#e0e0e0', 'lineColor': '#5a5a8a',
  'secondaryColor': '#3d3d5c', 'tertiaryColor': '#252540',
  'fontSize': '14px', 'darkMode': true
}}}%%
```

### Publication Grayscale
```
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#f5f5f5', 'primaryBorderColor': '#666666',
  'primaryTextColor': '#000000', 'lineColor': '#666666',
  'secondaryColor': '#ffffff', 'tertiaryColor': '#eeeeee',
  'fontSize': '12px', 'fontFamily': 'serif'
}}}%%
```

## Sequence Diagram Specific

```mermaid
%%{init: {'sequence': {
  'mirrorActors': false,
  'actorFontSize': 14,
  'noteFontSize': 12,
  'messageFontSize': 13,
  'width': 150,
  'height': 50,
  'boxMargin': 10
}}}%%
```

## Pie Chart Specific

```mermaid
%%{init: {'pie': {
  'textPosition': 0.75,
  'strokeWidth': 1
}}}%%
```

## Gantt Chart Specific

```mermaid
%%{init: {'gantt': {
  'titleTopMargin': 25,
  'barHeight': 20,
  'barGap': 4,
  'topPadding': 50,
  'leftPadding': 75,
  'gridLineStartPadding': 35,
  'fontSize': 11,
  'sectionFontSize': 14,
  'numberSectionStyles': 4
}}}%%
```
