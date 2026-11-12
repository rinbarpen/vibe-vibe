# Mermaid Reference

## Diagram Type Cheatsheet

| Type | Directive | Key Elements |
|------|-----------|-------------|
| Flowchart | `graph TD` / `graph LR` | `[rect]`, `(round)`, `{diamond}`, `((circle))`, `[[subroutine]]`, `[(db)]`, `>flag]` |
| Sequence | `sequenceDiagram` | `participant`, `->>`, `-->>`, `activate`, `Note`, `alt/else`, `loop` |
| Class | `classDiagram` | `class Name { }`, `<<interface>>`, `<<abstract>>`, `--|>`, `*--`, `-->` |
| State | `stateDiagram-v2` | `[*]`, `-->`, `state Name { }`, `[<<fork>>]`, `[<<join>>]` |
| ER | `erDiagram` | `ENTITY { type name PK/FK/UK "desc" }`, `||--o{`, `}o--||` |
| Gantt | `gantt` | `dateFormat`, `section`, `:done/:active/:crit/:milestone`, `after X` |
| Pie | `pie` / `pie showData` | `title`, `"Label" : value` |
| Git | `gitGraph` | `commit`, `branch`, `checkout`, `merge`, `cherry-pick`, `tag:` |
| Mindmap | `mindmap` | `root(( )))`, indentation for hierarchy, `::icon(fa fa-X)` |
| Timeline | `timeline` | `title`, `Section : Event : Event` |
| C4 | `C4Context` / `C4Container` | `Person()`, `System()`, `System_Ext()`, `Container()`, `Rel()` |
| Block | `block-beta` | `columns N`, `block:Name:N`, `space:N` |
| Sankey | `sankey-beta` | `Source, Target, Weight` |
| XY Chart | `xychart-beta` | `x-axis`, `y-axis`, `bar`, `line` |

## Node Shapes (Flowchart)

```
A[Rectangle]        — Standard process
B(Rounded)          — Start/End
C{Decision}         — Diamond, use for branching
D((Circle))         — Connector
E[[Subroutine]]     — Predefined process
F[(Database)]       — Data store
G>Flag]             — Input/Output
H{{Hexagon}}        — Preparation
I[/Parallelogram/]  — Manual input
J[\Parallelogram\]  — Manual operation
```

## Relationships (Class Diagram)

```
<|--     Inheritance (extends)
*--      Composition (has-a, strong)
o--      Aggregation (has-a, weak)
-->      Association
..>      Dependency
..|>     Realization (implements)
```

## ERD Relationship Notation

```
||--||   One to one
||--o{   One to zero-or-many
||--|{   One to one-or-many
}|--o{   Many to zero-or-many (default)
}o--o|   Zero-or-many to zero-or-one
```

## Styling

### Flowchart Nodes
```
style A fill:#dae8fc,stroke:#6c8ebf,color:#000
style B fill:#d5e8d4,stroke:#82b366
```

### Class Definitions (Reusable)
```
classDef primary fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px
class A,B,C primary
```

### Sequence Participant Box
```
participant A as [Custom Label]
Note over A,B: Annotation spanning A and B
```

## Live Preview

| Platform | How |
|----------|-----|
| [mermaid.live](https://mermaid.live) | Paste code → instant render → export PNG/SVG |
| GitHub | Code fence in `.md` file → auto-renders |
| Notion | `/code` block → select Mermaid |
| Obsidian | Native Mermaid plugin |
| VSCode | "Markdown Preview Mermaid Support" extension |
| CLI | `mmdc -i input.mmd -o output.png` (@mermaid-js/mermaid-cli) |

## CLI Export

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i diagram.mmd -o diagram.png -w 1200 -H 800 --backgroundColor white
mmdc -i diagram.mmd -o diagram.svg -w 1200  # SVG for vector
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Lexical error | Invalid character in label | Remove special chars or use quotes |
| Parse error on line X | Syntax typo | Check semicolons, arrow syntax |
| Subgraph not closing | Missing `end` | Add `end` after subgraph content |
| Text overflow | Long labels | Use `<br/>` for line breaks |
| Block diagram columns | Wrong count | Ensure `columns N` matches layout |
