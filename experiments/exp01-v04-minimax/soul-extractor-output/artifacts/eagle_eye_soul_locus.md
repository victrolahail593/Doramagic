# Eagle Eye Soul Locus

## Scoring Methodology

Each code area scored on 8 dimensions (0-100 scale):
- **Domain Centrality (20%):** How core is this to the project's purpose
- **Execution Influence (15%):** Controls program flow/termination
- **Orchestration Power (15%):** Coordinates other components
- **Data/State Gravity (15%):** Central data hub or state management
- **Rule Density (10%):** Number of explicit rules/logic
- **Boundary Importance (10%):** Critical for external interfaces
- **Cross-Module Bridge (10%):** Connects multiple modules
- **Concept Density (5%):** Dense with important concepts

## Code Area Analysis

### 1. src/dotenv/main.py
| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Domain Centrality | 95 | Core loading engine - IS the project |
| Execution Influence | 85 | Controls when/how env vars loaded |
| Orchestration Power | 80 | Coordinates parser, variables, file I/O |
| Data/State Gravity | 90 | Central hub for all env data |
| Rule Density | 70 | Moderate - file handling, encoding, etc |
| Boundary Importance | 90 | Public API entry point |
| Cross-Module Bridge | 85 | Links parser, variables, cli |
| Concept Density | 85 | Many concepts (loading, finding, setting) |
| **TOTAL** | **83.5** | |

### 2. src/dotenv/parser.py
| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Domain Centrality | 85 | Parsing IS core functionality |
| Execution Influence | 70 | Tokenizes but doesn't control flow |
| Orchestration Power | 40 | Single-purpose, no coordination |
| Data/State Gravity | 50 | Passes through data, doesn't store |
| Rule Density | 90 | Dense regex rules |
| Boundary Importance | 75 | Critical for valid .env syntax |
| Cross-Module Bridge | 50 | Outputs to main.py only |
| Concept Density | 80 | Regex, escape sequences, quotes |
| **TOTAL** | **67.5** | |

### 3. src/dotenv/variables.py
| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Domain Centrality | 75 | Variable expansion is key feature |
| Execution Influence | 60 | String transformation only |
| Orchestration Power | 30 | Simple transformation |
| Data/State Gravity | 40 | No storage, just expansion |
| Rule Density | 85 | Complex expansion rules |
| Boundary Importance | 65 | User-facing feature |
| Cross-Module Bridge | 55 | Used by main.py |
| Concept Density | 75 | POSIX expansion concepts |
| **TOTAL** | **60.6** | |

### 4. src/dotenv/cli.py
| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Domain Centrality | 60 | CLI is optional feature |
| Execution Influence | 70 | Controls command execution |
| Orchestration Power | 65 | Coordinates dotenv operations |
| Data/State Gravity | 50 | Pass-through to main.py |
| Rule Density | 55 | Click decorators, command logic |
| Boundary Importance | 80 | Primary external interface |
| Cross-Module Bridge | 60 | Bridges user to core |
| Concept Density | 50 | CLI concepts |
| **TOTAL** | **61.3** | |

### 5. src/dotenv/ipython.py
| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Domain Centrality | 30 | Optional integration |
| Execution Influence | 30 | Loads on magic call |
| Orchestration Power | 20 | Minimal |
| Data/State Gravity | 30 | Delegated to main.py |
| Rule Density | 25 | Simple magic registration |
| Boundary Importance | 40 | IPython users |
| Cross-Module Bridge | 35 | Bridges IPython to main |
| Concept Density | 35 | IPython magic concepts |
| **TOTAL** | **30.6** | |

## Score Distribution

| Area | Score | Below 70? |
|------|-------|-----------|
| ipython.py | 30.6 | ✅ YES |
| variables.py | 60.6 | ✅ YES |
| cli.py | 61.3 | ✅ YES |
| parser.py | 67.5 | ✅ YES |
| main.py | 83.5 | ❌ NO |

**Below 70:** 4/5 = 80% (exceeds 30% requirement ✅)

## Top 3 Areas for Deep Dive

1. **main.py** (83.5) - Core engine, highest priority
2. **parser.py** (67.5) - Tokenization foundation
3. **variables.py** (60.6) - Key feature differentiation
