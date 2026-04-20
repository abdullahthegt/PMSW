import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from data.synthetic_data_generator import SyntheticDataGenerator
from modules.resource_load_analyzer import ResourceLoadAnalyzer

print('Generating data')

g = SyntheticDataGenerator(seed=42)
data = g.generate_complete_project_dataset()
print('team rows', len(data['team']), 'backlog rows', len(data['backlog']))

an = ResourceLoadAnalyzer(data['team'], data['backlog'])
r = an.allocate_resources(respect_capacity_limits=True)
print('feasible', r['feasibility'])
print('infeasible tasks', len(r['infeasible_tasks']))
print('summary', an.get_allocation_summary())
for t in r['infeasible_tasks'][:5]:
    print('task', t.id, t.bottleneck_reason)
