import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path('.').resolve() / 'src'))
from modules.resource_load_analyzer import ResourceLoadAnalyzer

team_df = pd.DataFrame([{'ID':1,'Name':'Dev1','Role':'Dev','Skills':'C/C++;Embedded Systems','Availability_Hours':200,'Efficiency':1.0}])
tasks_df = pd.DataFrame([{'TaskID':i,'Title':f'T{i}','Type':'Code','ASIL':'B','EstimatedHours':5,'StoryPoints':5} for i in range(1,10)])

an=ResourceLoadAnalyzer(team_df,tasks_df)
result=an.allocate_resources(respect_capacity_limits=True)
print('feasible',result['feasibility'])
print('infeasible',len(result['infeasible_tasks']))
print(an.get_allocation_summary())
