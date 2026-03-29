import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))

from src.data.synthetic_data_generator import SyntheticDataGenerator
from src.modules.resource_load_analyzer import ResourceLoadAnalyzer

print('Generating data...')
g = SyntheticDataGenerator(seed=42)
data = g.generate_complete_project_dataset()

print('Creating analyzer...')
an = ResourceLoadAnalyzer(data['team'], data['backlog'])

print('Allocating resources...')
result = an.allocate_resources()
print('Success!')

print('\nAllocation DataFrame columns:', result['allocation_df'].columns.tolist())
print('DataFrame shape:', result['allocation_df'].shape)
print('\nFirst 5 rows:')
print(result['allocation_df'].head())
print('\nStatus value counts:')
print(result['allocation_df']['Status'].value_counts())
