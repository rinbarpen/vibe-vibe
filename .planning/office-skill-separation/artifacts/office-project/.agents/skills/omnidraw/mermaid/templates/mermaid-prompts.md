# Mermaid Prompt Templates

Copy-paste templates for all Mermaid diagram types.

---

## Flowchart

### Basic
```
Create a Mermaid graph TD:
A[Start] --> B[Process]; B --> C{Decision?};
C -->|Yes| D[Path A]; C -->|No| E[Path B];
D --> F[End]; E --> F.
Style A green, F blue, C yellow. Subgraph for related steps.
```

### With Subgraphs
```
Create a Mermaid graph LR with subgraphs:
subgraph Input ["Input Layer"]
  A[API] --> B[Parser]
end
subgraph Core ["Processing"]
  B --> C[Engine] --> D[(Cache)]
end
subgraph Output ["Output Layer"]
  D --> E[Renderer] --> F[Response]
end
```

---

## Sequence Diagram

### API Call
```
Create a Mermaid sequence diagram:
participant C as Client
participant G as API Gateway
participant S as Service
participant D as Database
C->>G: POST /endpoint
G->>S: forward request
S->>D: SELECT query
D-->>S: result set
S-->>G: response
G-->>C: JSON response
Note over S,D: Transaction boundary
```

### Auth Flow
```
Create a Mermaid sequence diagram for OAuth 2.0:
participant U as User
participant C as Client App
participant A as Auth Server
participant R as Resource Server
U->>C: Click login
C->>A: /authorize (redirect)
A->>U: Login page
U->>A: Credentials
A->>C: Auth code (redirect)
C->>A: /token (code + secret)
A-->>C: access_token + refresh_token
C->>R: GET /data (Bearer token)
R-->>C: Protected data
Note over C,A: PKCE recommended for SPAs
```

---

## Class Diagram

```
Create a Mermaid classDiagram for [domain]:
class BaseEntity {
  +String id
  +DateTime createdAt
  +DateTime updatedAt
}
class [EntityA] {
  +String [field]
  +int [field]
  +[method](param): returnType
}
class [EntityB] {
  +String [field]
  +[method](): returnType
}
[EntityA] "1" --> "*" [EntityB] : [relationship]
<<abstract>> BaseEntity
[EntityA] --|> BaseEntity
```

---

## State Diagram

```
Create a Mermaid stateDiagram-v2 for [entity/component]:
[*] --> Idle
Idle --> Loading : [trigger]
Loading --> Success : [ok condition]
Loading --> Error : [fail condition]
Error --> Loading : retry
Success --> [*]
state Loading {
  [*] --> Fetching
  Fetching --> Validating
  Validating --> [*]
}
```

---

## ER Diagram

```
Create a Mermaid erDiagram:
[EntityA] {
  uuid id PK "Primary key"
  string email UK "Unique email"
  string name "Display name"
  timestamp created_at
}
[EntityB] {
  uuid id PK
  uuid entity_a_id FK "References EntityA"
  float amount
  string status
}
[EntityA] ||--o{ [EntityB] : "has many"
```

---

## Gantt Chart

```
Create a Mermaid gantt chart:
title [Project] Plan
dateFormat YYYY-MM-DD
axisFormat %m/%d
section [Phase 1]
[Task 1] :done, t1, 2026-01-01, 14d
[Task 2] :active, t2, after t1, 10d
section [Phase 2]
[Task 3] :t3, after t2, 21d
[Task 4] :crit, t4, after t3, 7d
[Milestone] :milestone, m1, after t4, 0d
```

---

## Pie Chart

```
Create a Mermaid pie chart:
title [Distribution Title]
"[Category A]" : 40
"[Category B]" : 30
"[Category C]" : 20
"[Category D]" : 10
```

---

## Git Graph

```
Create a Mermaid gitGraph:
commit id: "init"
branch develop
checkout develop
commit id: "setup"
branch feature/login
checkout feature/login
commit id: "add login form"
commit id: "add validation"
checkout develop
merge feature/login
branch release/v1
checkout release/v1
commit id: "version bump" tag: "v1.0.0"
checkout main
merge release/v1
```

---

## Mind Map

```
Create a Mermaid mindmap:
root(("[Project Name]"))
  [Category A]
    [Sub A1]
      [Detail X]
      [Detail Y]
    [Sub A2]
  [Category B]
    [Sub B1]
    [Sub B2]
  [Category C]
```

---

## Timeline

```
Create a Mermaid timeline:
title [Project] Timeline
[Year/Phase] : [Event 1] : [Event 2] : [Event 3]
[Year/Phase] : [Event 4] : [Event 5]
[Year/Phase] : [Event 6]
```

---

## C4 Architecture

### System Context
```
Create a Mermaid C4Context:
title System Context for [System Name]
Person([user], "[Role]", "[Description]")
System([system], "[Name]", "[Description]")
System_Ext([ext], "[External Name]", "[Description]")
Rel([user], [system], "[Uses]", "[Protocol]")
Rel([system], [ext], "[Calls]", "[Protocol]")
```

### Container
```
Create a Mermaid C4Container:
Container([web], "Web App", "React", "User-facing SPA")
Container([api], "API", "Go", "REST API")
ContainerDb([db], "Database", "PostgreSQL", "Primary store")
Rel([web], [api], "HTTPS/JSON")
Rel([api], [db], "SQL/TCP")
```

---

## Block Diagram

```
Create a Mermaid block-beta:
columns 3
block:Frontend:3
  [Web App]
  [Mobile App]
end
block:Backend:3
  [API Gateway]
  [Services]
  [Workers]
end
space:3
[Database] space [Cache]
```

---

## Sankey

```
Create a Mermaid sankey-beta:
[Source A], [Target X], 100
[Source A], [Target Y], 50
[Source B], [Target X], 30
[Source B], [Target Z], 70
```
