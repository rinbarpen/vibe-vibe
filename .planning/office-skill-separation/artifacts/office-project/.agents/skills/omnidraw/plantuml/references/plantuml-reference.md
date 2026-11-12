# PlantUML Reference

## Rendering Options

| Method | Command / URL |
|--------|--------------|
| Online server | `https://www.plantuml.com/plantuml/uml/[encoded]` |
| Local CLI | `java -jar plantuml.jar diagram.puml` |
| VSCode | PlantUML extension |
| Docker | `docker run -v $PWD:/data plantuml/plantuml diagram.puml` |
| npm | `npx node-plantuml diagram.puml` |

## Diagram Types

| Type | Directive | Best For |
|------|-----------|----------|
| Class | `@startuml` + class/interface/abstract | OOP design, domain models |
| Use Case | `@startuml` + actor/usecase | Requirements, system scope |
| Activity | `@startuml` + start/stop/if/repeat | Business processes, workflows |
| Component | `@startuml` + component/package | Software architecture |
| Deployment | `@startuml` + node/cloud | Infrastructure, topology |
| Sequence* | `@startuml` + participant/-> | API flows (use Mermaid instead) |
| State* | `@startuml` + state/[*] | State machines (use Mermaid instead) |
| Timing | `@startuml` + concise/@time | Concurrent state over time |
| Object | `@startuml` + object | Instance snapshots |

*Mermaid is preferred for sequence and state diagrams.

## Relationship Notation (Class Diagram)

```
<|--      Extension (inheritance)
*--       Composition (strong ownership)
o--       Aggregation (weak ownership)
-->       Association
..>       Dependency
..|>      Implementation (implements interface)

Cardinality: "1", "0..1", "0..*", "1..*", "*" (default)
Position: ClassA "1" -- "*" ClassB : label
```

## Use Case Notation

```
-->       Association (actor to use case)
.>        Dependency (use case to use case)
<.        Extension (extends — optional behavior)
<|--      Generalization (actor inheritance)

Position: U1 --> UC1 : "trigger"
```

## Activity Notation

```
start     Entry point
stop      Exit point
end       Flow termination
:Text;    Action/activity
if/else/endif   Conditional
repeat/repeat while   Loop
while/endwhile   While loop
fork/fork again/end fork   Parallel
split/split again/end split   Alternative
->        Flow
note left/right   Annotation
partition "Name" { }   Swimlane
```

## Component Notation

```
[Name]        Component
component "Name"   Named component
() "Name"     Interface
package "Name" { }  Package/namespace
node "Name" { }     Node (deployment)
database "Name"     Database
cloud "Name" { }    Cloud (deployment)
```

## Styling

```
!theme plain
!theme cerulean
!theme superhero
!theme sketchy-outline

skinparam backgroundColor #FFFFFF
skinparam classBackgroundColor #dae8fc
skinparam classBorderColor #6c8ebf
skinparam arrowColor #666666
skinparam defaultFontSize 14
skinparam defaultFontName system-ui

hide empty members
hide circle (for use case "stick figure" style)
skinparam handwritten true (sketchy style)
```

## PlantUML vs Mermaid

| Feature | PlantUML | Mermaid |
|---------|----------|---------|
| Class diagram | Best | Basic |
| Use case diagram | Yes | No |
| Activity diagram | Best | Flowchart only |
| Component diagram | Yes | No (block-beta) |
| Deployment diagram | Yes | No |
| Timing diagram | Yes | No |
| Sequence diagram | Good | Better |
| State diagram | Good | Better |
| ERD | Good (IE notation) | Better (crow's foot) |

**Rule**: UML → PlantUML. Quick embeddable → Mermaid. Architecture → Draw.io.
