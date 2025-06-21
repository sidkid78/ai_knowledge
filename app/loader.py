import json

# Test loading the workflow
with open('app/api/v1/simulation_workflow.json', 'r') as f:
    workflow = json.load(f)
    
print(f"Workflow: {workflow['name']}")
print(f"Axes: {len(workflow['axisMapping']['axes'])}")
print(f"Layers: {len(workflow['simulationStack'])}")