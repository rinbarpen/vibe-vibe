# PlantUML Prompt Templates

Copy-paste prompts for each UML diagram type.

---

## Class Diagram

```
Create a PlantUML class diagram for [domain]:
class [EntityA] {
  +String id
  -String [privateField]
  +[method](param: Type): ReturnType
}
class [EntityB] {
  +String id
  +[method](): Type
}
[EntityA] "1" -- "*" [EntityB] : [relationship]
abstract class [AbstractClass] { }
interface [Interface] { }
[EntityA] --|> [AbstractClass]
[EntityB] ..|> [Interface]
```

## Use Case Diagram

```
Create a PlantUML use case diagram:
left to right direction
actor [UserRole1] as U1
actor [UserRole2] as U2
usecase "[UC1]" as UC1
usecase "[UC2]" as UC2
usecase "[UC3]" as UC3
U1 --> UC1
U1 --> UC2
U2 --> UC3
UC2 <. UC3 : <<extend>>
UC1 .> UC3 : <<include>>
```

## Activity Diagram

```
Create a PlantUML activity diagram:
start
:[Step 1];
if ([Condition]?) then (yes)
  :[True branch action];
else (no)
  :[False branch action];
endif
:[Step 2];
repeat
  :[Loop action];
repeat while ([Loop condition]?)
:[Final step];
stop
```

## Component Diagram

```
Create a PlantUML component diagram:
package "[Frontend Package]" {
  [Web App] as web
  [Mobile App] as mobile
}
package "[Backend Package]" {
  [API Gateway] as gw
  [Auth Service] as auth
  database "[Database Name]" as db
}
web --> gw : REST
mobile --> gw : REST
gw --> auth : gRPC
gw --> db : SQL
```

## Deployment Diagram

```
Create a PlantUML deployment diagram:
node "[Server Name]" {
  node "[Container/VM]" {
    [Component A]
    [Component B]
  }
}
node "[Cloud Region]" as cloud {
  node "[Service]" {
    [Component C]
  }
}
cloud -- [Server Name] : [Protocol]
```

## Timing Diagram

```
Create a PlantUML timing diagram:
concise "[Participant A]" as A
concise "[Participant B]" as B
@0
A is [State1]
B is [State1]
@[time]
A is [State2]
@[time]
B is [State2]
@[time]
A is [State1]
B is [State1]
```
