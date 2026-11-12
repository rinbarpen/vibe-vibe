# Visio References

## Diagram Type ↔ Visio Template Mapping

| Diagram | Visio Template | Tab Location |
|---------|---------------|-------------|
| Flowchart | Basic Flowchart | Flowchart |
| Cross-functional flowchart | Cross-Functional Flowchart | Flowchart |
| BPMN | BPMN Diagram | Flowchart |
| Org chart | Organization Chart | Business |
| Network diagram | Detailed Network Diagram | Network |
| Rack diagram | Rack Diagram | Network |
| UML Class | UML Class | Software |
| UML Sequence | UML Sequence | Software |
| UML Use Case | UML Use Case | Software |
| UML Component | UML Component | Software |
| Database ERD | Crow's Foot DB Notation | Software |
| Floor plan | Floor Plan | Maps & Floor Plans |
| Office layout | Office Layout | Maps & Floor Plans |
| Timeline | Timeline | Schedule |
| Gantt chart | Gantt Chart | Schedule |
| Calendar | Calendar | Schedule |
| Basic shapes | Basic Diagram | General |

## Visio Stencil Sources

| Source | URL | Content |
|--------|-----|---------|
| Microsoft 365 | Built-in | General, business, software, network |
| AWS | aws.amazon.com/architecture/icons | AWS service icons |
| Azure | docs.microsoft.com/azure/architecture/icons | Azure service icons |
| GCP | cloud.google.com/icons | Google Cloud icons |
| Cisco | cisco.com (network topologies) | Network equipment |
| VMware | vmware.com (solution exchange) | Virtualization |

## Draw.io → Visio Mapping

| Draw.io Shape | Visio Equivalent | Notes |
|---------------|-----------------|-------|
| Rectangle (Process) | Process (Basic Flowchart) | Direct mapping |
| Rounded Rectangle | Process (rounded) | May lose rounding |
| Diamond (Decision) | Decision (Basic Flowchart) | Direct mapping |
| Cylinder (Database) | Database (Software) | Direct mapping |
| Cloud shape | Cloud (Network) | Direct mapping |
| Swimlane container | CFF Swimlane | Direct mapping |
| UML Class | UML Class | May need adjustment |
| BPMN shapes | BPMN shapes | Generally good fidelity |
| Custom icons | May need manual replacement | Use Visio stencils instead |

## Visio Export Formats

| From | Format | Use Case |
|------|--------|----------|
| Visio | VSDX | Native, editable |
| Visio | PDF | Vector, review/print |
| Visio | PNG | Raster, embed in docs |
| Visio | SVG | Vector, web |
| Visio | DWG | CAD interop |
| Draw.io | VSDX | Bridge from Draw.io |

## Visio Limitations (vs Draw.io)

- No MCP/API for programmatic generation
- No real-time browser preview
- No live collaboration (requires SharePoint)
- Stencil discovery is manual
- Export fidelity: Draw.io→VSDX may need minor fixes
- Font substitution possible if fonts not installed
