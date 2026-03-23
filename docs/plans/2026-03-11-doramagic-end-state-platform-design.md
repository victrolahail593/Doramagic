# Doramagic End-State Platform Design

Date: 2026-03-11
Status: Draft

## 1. Positioning

Doramagic is not a knowledge extraction tool, and it is not just a skill generator.
Its end-state form is:

An OpenClaw-native platform for personalized agent assembly and evolution.

Its job is to continuously absorb best practices from open-source ecosystems, combine them with OpenClaw-native capabilities and user-specific suitability signals, and compile them into executable, verifiable, and improvable agent artifacts.

## 2. Core Value

Doramagic solves three problems at once:

1. Users often cannot clearly describe the most suitable solution for themselves.
2. General-purpose AI can answer questions, but usually cannot deliver a stable, personalized, executable agent outcome.
3. High-quality open-source "homework" exists, but it is noisy, fragmented, and difficult to turn into reusable capability assets.

Doramagic's value chain is:

Discover best practice -> Extract structured capability knowledge -> Match to user suitability -> Compile executable artifact -> Observe use -> Improve continuously

## 3. Architecture Principles

- Graph-first, vector-assisted
- Compile, do not just prompt
- Online runtime consumes processed knowledge; offline pipelines produce it
- Suitability is more important than generic best
- Confidence must be backed by evidence
- Runtime uses a state machine, not a fixed linear pipeline

## 4. Top-Level Architecture

```text
User / OpenClaw
    ->
Gateway / Interaction
    ->
Orchestrator
    -> Knowledge Fabric
    -> Suitability Engine
    -> Assembly Compiler
    -> Validation Service
    -> Delivery

Offline Knowledge Plane:
Sources
    -> Ingestion
    -> Extraction
    -> Normalization
    -> Quality Filtering
    -> Knowledge Fabric
```

The system has two planes:

- Knowledge Factory: produces structured platform knowledge assets
- Agent Runtime: assembles and delivers personalized artifacts in real time

The shared core is the Knowledge Fabric.

## 5. Service Decomposition

### 5.1 Gateway / Interaction Service

Responsibilities:

- Receive user input, session context, and history
- Manage clarification turns and confidence-based interaction depth
- Return candidate options and final deliverables

### 5.2 Orchestrator Service

Responsibilities:

- Drive the runtime state machine
- Split high-level requests into tasks
- Handle fallback, retries, and state transitions
- Coordinate synchronous request flow and asynchronous jobs

Recommended stack:

- Temporal
- FastAPI
- Python workers

### 5.3 Knowledge Ingestion Service

Responsibilities:

- Connect to GitHub repositories, issues, discussions, docs, existing skills, MCP servers, APIs, and execution traces
- Run incremental sync and deduplication
- Produce raw source artifacts

### 5.4 Knowledge Extraction Service

Responsibilities:

- Extract concepts, workflows, decision rules, pitfalls, capabilities, dependencies, and resources
- Produce structured knowledge objects plus evidence references

### 5.5 Knowledge Fabric Service

Responsibilities:

- Provide unified query APIs to upper layers
- Hide graph/vector/document storage complexity
- Maintain indexing, lineage, versions, and evidence chains

### 5.6 Suitability Engine

Responsibilities:

- Model user preferences, risk tolerance, explanation style, and repeated success patterns
- Rank candidates by user fit instead of generic optimality

### 5.7 Assembly / Compiler Service

Responsibilities:

- Assemble knowledge and capability objects into delivery artifacts
- Generate skills, skill bundles, MCP configs, workflows, or agent profiles

### 5.8 Validation & Observation Service

Responsibilities:

- Validate schema, dependency, runtime readiness, and trust
- Observe post-delivery execution and feedback
- Feed learning signals back to the platform

## 6. Knowledge Fabric

The Knowledge Fabric is the core strategic asset of Doramagic.
It should not be a single database. It should be a unified knowledge layer built on multiple storage systems.

### 6.1 Storage Components

#### Postgres

Stores:

- users
- sessions
- artifacts metadata
- registries
- validation reports
- event projections

#### Neo4j

Stores:

- project relationships
- concept links
- workflow and dependency edges
- pitfall-to-solution relations
- capability compatibility
- user suitability relations
- execution graph links

#### Qdrant

Stores:

- document embeddings
- knowledge object embeddings
- issue/discussion summary embeddings
- task-pattern embeddings

#### Object Store

Stores:

- raw crawled artifacts
- repo snapshots
- issue/discussion dumps
- evidence payloads
- generated artifact payloads
- trace attachments

### 6.2 Query Broker

Upper layers must not talk directly to raw stores.
The Knowledge Fabric exposes a unified query broker that supports:

- semantic retrieval
- graph traversal
- metadata filters
- evidence filters
- reranking

## 7. Canonical Object Model

### 7.1 KnowledgeObject

Core fields:

- id
- type: concept | workflow | decision_rule | pitfall | capability_resource
- title
- summary
- description
- tags
- source_refs
- evidence_level
- freshness_score
- confidence_score
- applicability
- dependencies
- related_objects
- created_at
- updated_at

### 7.2 CapabilityResource

Core fields:

- id
- capability_name
- kind: skill | mcp_tool | api | cli | workflow_step
- inputs
- outputs
- dependencies
- invocation
- constraints
- install_spec

### 7.3 UserSuitabilityProfile

Core fields:

- user_id
- interaction_depth
- explanation_style
- risk_tolerance
- tool_affinity
- preferred_models
- avoided_tools
- acceptance_rate
- edit_rate
- execution_success_rate
- recurring_scenarios

### 7.4 DeliveryArtifact

Core fields:

- artifact_id
- type: skill | skill_bundle | mcp_config | workflow | agent_profile
- generated_from
- payload_ref
- validation_status
- trust_label
- install_ready

### 7.5 ExecutionTrace

Core fields:

- trace_id
- user_id
- request
- states
- inputs
- outputs
- failures
- feedback
- timestamps

## 8. Runtime State Machine

Doramagic runtime should be implemented as a re-entrant state machine:

```text
Understand
-> Discover
-> Compose
-> Validate
-> Deliver
-> Observe
-> Evolve
```

Fallback rules:

- If intent confidence is low, return to Understand
- If evidence is insufficient, return to Discover
- If validation fails, return to Compose

This is fundamentally different from a static batch pipeline.

## 9. Online and Offline Flows

### 9.1 Online Runtime Flow

```text
user request
-> orchestrator
-> fabric retrieval
-> suitability ranking
-> assembly compile
-> validation
-> delivery
-> feedback
```

Goal:

- Fast delivery of executable and personalized results
- Minimal heavy online research

### 9.2 Offline Knowledge Production Flow

```text
source discovery
-> ingestion
-> extraction
-> normalization
-> quality filtering
-> fabric write
-> index refresh
```

Goal:

- Continuously improve the platform's knowledge assets
- Raise runtime precision and trustworthiness over time

## 10. Deliverables

Doramagic should standardize four artifact types:

- Expert Skill
- Skill Bundle
- MCP Config
- Agent Workflow / Agent Profile

Every artifact should include:

- manifest
- dependency spec
- install readiness
- trust label
- explainability summary

## 11. Validation Architecture

Validation should be layered:

### 11.1 Structural Validation

- Schema correctness
- Reference completeness
- Manifest integrity

### 11.2 Dependency Validation

- env vars
- binaries
- permissions
- model availability
- tool availability

### 11.3 Execution Validation

- smoke execution
- happy-path readiness checks

### 11.4 Trust Calibration

Trust score should be derived from:

- evidence quality
- source consistency
- validation results
- historical success rate

Possible outputs:

- pass
- partial
- fail
- setup_required
- ready_to_install
- trust: high | medium | low

## 12. Events

The platform should be event-driven. Core events include:

- request_received
- intent_understood
- clarification_required
- candidates_retrieved
- candidates_ranked
- artifact_compiled
- validation_passed
- validation_failed
- artifact_delivered
- artifact_accepted
- artifact_edited
- artifact_rejected
- execution_observed
- knowledge_ingested
- knowledge_extracted
- knowledge_reindexed

These events support:

- learning loops
- trace replay
- debugging
- analytics
- A/B testing

## 13. Technology Choices

Recommended end-state stack:

- API Layer: FastAPI
- Workflow Orchestration: Temporal
- Primary DB: Postgres
- Vector Store: Qdrant
- Graph Store: Neo4j
- Object Store: S3-compatible storage
- Async Workers: Python
- Query Layer: custom Query Broker
- Ranking: BM25 + embedding + rerank + suitability
- Model Routing: custom Model Gateway

### 13.1 Must Build In-House

- Query Broker
- Suitability Engine
- Assembly Compiler
- Validation Policy Engine
- Canonical Schemas
- Artifact Manifest Model

### 13.2 Should Not Build In-House

- workflow engine
- vector DB
- graph DB
- object store
- GitHub basic ingestion plumbing

## 14. Evolution Roadmap

### Phase 0: Schema First

Define:

- KnowledgeObject
- CapabilityResource
- DeliveryArtifactManifest
- UserSuitabilityProfile
- ExecutionTrace

### Phase 1: Minimal Runtime Loop

Scope:

- single user
- single workspace
- simple retrieval
- request -> retrieve -> rank -> compile -> validate -> deliver

Implementation:

- Postgres
- object store
- simplified retrieval
- no full graph yet

### Phase 2: Knowledge Fabric Formation

Add:

- Qdrant
- Query Broker
- multi-source extraction
- evidence scoring
- capability registry

### Phase 3: Relationship and Suitability Upgrade

Add:

- Neo4j
- User Suitability Graph
- Execution Graph
- graph-assisted retrieval
- artifact evolution and comparison

### Phase 4: Platform Ecosystem

Add:

- multi-user
- multi-tenant
- shared knowledge marketplace
- automated revalidation
- cross-user capability reuse

## 15. Architecture Red Lines

Three things must not go wrong:

### 15.1 Do Not Let the Object Model Drift

cards, blocks, resources, and knowledge units must converge to one canonical object model.

### 15.2 Do Not Couple Runtime to Raw Online Research

If every user request triggers heavy GitHub research, the system will be slow, expensive, and unstable.

### 15.3 Do Not Reduce Personalization to Prompt Tricks

Suitability must be an explicit system model, not an implicit prompt habit.

## 16. Final Conclusion

Doramagic should be built as:

A Knowledge-Fabric-centered, Orchestrator-driven, Suitability-aware, Compiler-based, Validation-backed Agent Infrastructure Product.

Its long-term moat is not the model alone. It comes from four compounding capabilities:

- knowledge production
- structured representation
- user suitability modeling
- execution feedback loops
