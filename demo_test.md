## AI Knowledge Discovery Demo

### Node Analysis
- **Node**: Quantum Computing Fundamentals  
- **Description**: Basic principles of quantum computing and qubits  
- **Axis Values**:
  - `pillar_function`: {'values': [0.9], 'weights': [1.0]}
  - `level_hierarchy`: {'values': [1.0], 'time_deltas': [1.0]}
  - `unified_system_function`: {'values': [0.8], 'weights': [1.0]}

**Running algorithm**: AI Knowledge Discovery

### Debug Information
#### Original Axis Values
- `pillar_function`: {'values': [0.9], 'weights': [1.0]}
- `level_hierarchy`: {'values': [1.0], 'time_deltas': [1.0]}
- `unified_system_function`: {'values': [0.8], 'weights': [1.0]}

#### Schema Conversions
**pillar_function**:
```python
Schema values: {'values': [0.9], 'weights': [1.0], 'time_deltas': [], 'parameters': {}}
Final schema: values=[0.9] weights=[1.0] time_deltas=[] parameters={}
```

**level_hierarchy**:
```python
Schema values: {'values': [1.0], 'weights': [1.0], 'time_deltas': [1.0], 'parameters': {}}
Final schema: values=[1.0] weights=[1.0] time_deltas=[1.0] parameters={}
```

**unified_system_function**:
```python
Schema values: {'values': [0.8], 'weights': [1.0], 'time_deltas': [], 'parameters': {}}
Final schema: values=[0.8] weights=[1.0] time_deltas=[] parameters={}
```

#### Input Data
```json
{
  "parameters": {
    "axis_parameters": [
      {"axis": "pillar_function", "required": true, "weight": 1.0},
      {"axis": "level_hierarchy", "required": true, "weight": 0.8}
    ]
  },
  "axis_values": {
    "pillar_function": AxisSchema(...),
    "level_hierarchy": AxisSchema(...),
    "unified_system_function": AxisSchema(...)
  }
}
```

#### Processing Results
```json
{
  "value": 0.8333333333333334,
  "confidence": 0.8333333333333334,
  "metadata": {
    "node_id": "3ad75d2d-f056-4813-b177-f9ca4109c518",
    "discoveries": [
      "HIGH_SIGNIFICANCE_PILLAR_FUNCTION",
      "MEDIUM_SIGNIFICANCE_LEVEL_HIERARCHY"
    ],
    "axis_contributions": {
      "pillar_function": 0.9,
      "level_hierarchy": 0.8,
      "unified_system_function": 0.8
    }
  },
  "warnings": []
}
```

### Final Results
**Confidence**: 0.83  
**Axis Contributions**:
1. pillar_function: 0.90
2. level_hierarchy: 0.80
3. unified_system_function: 0.80

**Discoveries**:
- HIGH_SIGNIFICANCE_PILLAR_FUNCTION
- MEDIUM_SIGNIFICANCE_LEVEL_HIERARCHY

---

## Risk Assessment Demo

### Risk Analysis
**Assessing risks for**: Quantum Computing Fundamentals

### Debug Information
#### Original Axis Values
- `pillar_function`: {'values': [0.9], 'weights': [1.0]}
- `level_hierarchy`: {'values': [1.0], 'time_deltas': [1.0]}
- `unified_system_function`: {'values': [0.8], 'weights': [1.0]}

#### Schema Conversions
(Same schema conversions as previous demo)

#### Input Data
```json
{
  "parameters": {
    "axis_parameters": [
      {"axis": "unified_system_function", "required": true, "weight": 1.0}
    ]
  }
}
```

#### Processing Results
```json
{
  "value": 0.8,
  "confidence": 0.3333333333333333,
  "metadata": {
    "risk_factors": ["HIGH_RISK_UNIFIED_SYSTEM_FUNCTION"],
    "axis_risks": {"unified_system_function": 0.8}
  },
  "warnings": ["Missing required axis: risk_tensor"]
}
```

### Final Results
**Risk Level**: 0.80  
**Risk Factors**: HIGH_RISK_UNIFIED_SYSTEM_FUNCTION  
**Axis Risks**:
- unified_system_function: 0.80

---

## Persona Agent Demo Error

```python
Traceback (most recent call last):
  [Full traceback...]
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) 
column persona_agents.state does not exist
LINE 1: ...available AS persona_agents_algorithms_available, persona_ag...
                                                             ^
```

**SQL Query**:
```sql
SELECT persona_agents.id, persona_agents.name, persona_agents.domain_coverage,
persona_agents.algorithms_available, persona_agents.state  -- Error here
FROM persona_agents
WHERE persona_agents.name = 'Quantum Computing Specialist'
LIMIT 1
```

**Error Context**:
- Missing database column: `persona_agents.state`
- Occurs during agent lookup by name
- SQLAlchemy model expects non-existent column