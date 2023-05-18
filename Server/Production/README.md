# Production demo

## Requirements
- (Python 3.10)
- Install pandas (`pip install pandas`)
- Solar demo requires:
    - "Plant_1_Generation" dataset from https://www.kaggle.com/datasets/anikannal/solar-power-generation-data 
- Wind demo requires:
    - The 2022 dataset from https://zenodo.org/record/7348454#.ZCp9OfZBxD9

### Example code
```
from Prod_device import Solar_power_device_demo
dev = Solar_power_device_demo()
current_Production = dev.get_power()
```