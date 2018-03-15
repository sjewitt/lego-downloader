import requests
from legoPlansClass import LegoPlans

plans = LegoPlans()
 
print(plans.planData)

# _res = requests.post('http://localhost:9090/GetStates', json={'filter': 'calif'})
# print(_res.content)