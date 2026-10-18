---
name: plantuml
description: PlantUML text-to-diagram for UML diagrams. Class, use case, activity, component, deployment, timing diagrams. Best UML coverage among text-to-diagram tools. Inline code fence generation — zero deps.
---

# PlantUML

Text-to-diagram for UML and beyond. Best-in-class UML coverage — class, use case, activity, component, deployment, timing, and more.

## When to Use

- UML class diagrams (best in class)
- Use case diagrams (only text-to-diagram tool with native support)
- Activity diagrams and business process models
- Component and deployment diagrams
- Timing diagrams
- When Mermaid's UML support is insufficient

**Not for**: flowcharts (use [mermaid](../mermaid/SKILL.md)), precise layouts (use [mermaid](../mermaid/SKILL.md)).

## Rendering Options

- https://www.plantuml.com/plantuml/ (online server)
- VSCode "PlantUML" extension
- `plantuml` CLI: `java -jar plantuml.jar diagram.puml`

## Diagram Types

### Class Diagram
```plantuml
@startuml
class User {
    +String id
    +String email
    +login(): Session
}
class Order {
    +String orderId
    +calculateTotal(): float
}
User "1" -- "*" Order : places
@enduml
```

### Use Case Diagram
```plantuml
@startuml
left to right direction
actor Customer
actor Admin
usecase "Browse" as UC1
usecase "Order" as UC2
usecase "Manage" as UC3
Customer --> UC1
Customer --> UC2
Admin --> UC3
@enduml
```

### Activity Diagram
```plantuml
@startuml
start
:User submits form;
if (Valid?) then (yes)
  :Create session;
  :Redirect;
else (no)
  :Show error;
  :Return;
endif
stop
@enduml
```

### Component Diagram
```plantuml
@startuml
package "Frontend" {
    [Web App] as web
    [Mobile] as mobile
}
package "Backend" {
    [API Gateway] as gw
    [Auth] as auth
    database "DB" as db
}
web --> gw
mobile --> gw
gw --> auth
gw --> db
@enduml
```

### Deployment Diagram
```plantuml
@startuml
node "AWS us-east-1" {
    node "ECS" {
        [Container A]
        [Container B]
    }
    database "RDS" {
        [Primary]
    }
}
@enduml
```

### Timing Diagram
```plantuml
@startuml
concise "Browser" as WB
concise "Server" as API
@0
WB is Requesting
API is Idle
@100
WB is Waiting
API is Processing
@200
WB is Rendering
API is Idle
@enduml
```

## Templates

```
Class diagram:
  Create a PlantUML class diagram: [EntityA] with fields [type name], methods [method()]. Relationships: [EntityA] "1" -- "*" [EntityB].

Use case:
  Create a PlantUML use case diagram: actors [list], use cases [list]. Show which actor triggers which use case.

Activity:
  Create a PlantUML activity diagram: start → [step1] → if([condition]) → [true path] / [false path] → end.

Component:
  Create a PlantUML component diagram: packages [A, B], components [X, Y, Z], interfaces, dependencies.

Deployment:
  Create a PlantUML deployment diagram: nodes [server1, server2], artifacts deployed to each, communication paths.
```
