## AI Knowledge Discovery Demo

### Analyzing Node

**Name:** Quantum Computing Fundamentals  
**Description:** Basic principles of quantum computing and qubits

### Axis Values

```python
- pillar_function: {'values': [0.9], 'weights': [1.0]}
- level_hierarchy: {'values': [1.0], 'time_deltas': [1.0]}
- unified_system_function: {'values': [0.8], 'weights': [1.0]}
```

### Algorithm Execution

**Running:** AI Knowledge Discovery

#### Debug Logs

1. **Original Axis Values:**

   ```python
   - pillar_function: {'values': [0.9], 'weights': [1.0]}
   - level_hierarchy: {'values': [1.0], 'time_deltas': [1.0]}
   - unified_system_function: {'values': [0.8], 'weights': [1.0]}
   ```

2. **Schema Conversions:**
   - pillar_function:

     ```python
     Schema values: {'values': [0.9], 'weights': [1.0], 'time_deltas': [], 'parameters': {}}
     Final schema: values=[0.9] weights=[1.0] time_deltas=[] parameters={}
     ```

   - level_hierarchy:

     ```python
     Schema values: {'values': [1.0], 'weights': [1.0], 'time_deltas': [1.0], 'parameters': {}}
     Final schema: values=[1.0] weights=[1.0] time_deltas=[1.0] parameters={}
     ```

   - unified_system_function:

     ```python
     Schema values: {'values': [0.8], 'weights': [1.0], 'time_deltas': [], 'parameters': {}}
     Final schema: values=[0.8] weights=[1.0] time_deltas=[] parameters={}
     ```

3. **Input Data:**

   ```python
   Parameters: {'axis_parameters': [
       {'axis': 'pillar_function', 'required': True, 'weight': 1.0},
       {'axis': 'level_hierarchy', 'required': True, 'weight': 0.8}
   ]}
   Axis values: {
       'pillar_function': AxisSchema(values=[0.9], weights=[1.0]),
       'level_hierarchy': AxisSchema(values=[1.0], time_deltas=[1.0]),
       'unified_system_function': AxisSchema(values=[0.8])
   }
   ```

### Results

**Confidence:** 0.83  
**Axis Contributions:**

- pillar_function: 0.90
- level_hierarchy: 0.80 
- unified_system_function: 0.80

**Discoveries:**

1. HIGH_SIGNIFICANCE_PILLAR_FUNCTION
2. MEDIUM_SIGNIFICANCE_LEVEL_HIERARCHY

---

## Risk Assessment Demo

### Assessment Target

**Node:** Quantum Computing Fundamentals

#### Debug Logs

1. **Original Axis Values:**

   ```python
   - pillar_function: {'values': [0.9], 'weights': [1.0]}
   - level_hierarchy: {'values': [1.0], 'time_deltas': [1.0]}
   - unified_system_function: {'values': [0.8], 'weights': [1.0]}
   ```

2. **Schema Conversions** (Same as Knowledge Discovery)

3. **Input Data:**

   ```python
   Parameters: {'axis_parameters': [
       {'axis': 'unified_system_function', 'required': True, 'weight': 1.0}
   ]}
   ```

### Results

**Risk Level:** 0.80  
**Risk Factors:** HIGH_RISK_UNIFIED_SYSTEM_FUNCTION  
**Axis Risks:**

- unified_system_function: 0.80

**Warnings:**

1. Missing required axis: risk_tensor

---

## Persona Agent Demo

**Persona:** Quantum Computing Specialist  
**State:** idle

### Domain Coverage

1. Computer Science (PL02)
2. Quantum Computing (PL07)

### Available Algorithms

1. AI Knowledge Discovery (v1.0)
2. Risk Assessment (v1.0)