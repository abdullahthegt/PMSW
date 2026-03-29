import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))

from data.synthetic_data_generator import SyntheticDataGenerator
from modules.resource_load_analyzer import ResourceLoadAnalyzer

print('Generating data...')
g = SyntheticDataGenerator(seed=42)
data = g.generate_complete_project_dataset()

print('Creating analyzer...')
an = ResourceLoadAnalyzer(data['team'], data['backlog'])

print('Allocating resources...')
try:
    result = an.allocate_resources()
    print('Success!')
    print(result.keys())
except Exception as e:
    print(f'Error: {type(e).__name__}')
    print(f'Message: {e}')
    import traceback
    traceback.print_exc()
