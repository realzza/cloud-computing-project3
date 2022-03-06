import numpy as np
from typing import Dict, Any

    
def handler(data: dict, context: object) -> Dict[str, Any]:
    
    records = {}
    cpu_env = {}
    # for the first time, cpu_env will be initialized, afterwards it can be directly retrieved and updated
    if getattr(context, "cpu_env", None) is None:
        n_cpus = 0
        for i in range(100):
            if not "cpu_percent-%d"%i in data:
                break
            n_cpus += 1
            
    assert n_cpus > 0, "problematic data stream stored in redis. Please contract maintainer for assistance"
    cpu_env["cpu_count"] = n_cpus
    for i in range(n_cpus):
        # cpu_env[i].append(data['cpu_percent-%d'%i])
        curr_data = data['cpu_percent-%d'%i]
        records['cpu_%d_1min_avg'] = np.mean(curr_data[-12:])
        records['cpu_%d_1h_avg'] = np.mean(curr_data[-720:])
    
    records['VM_used_past_5min_avg'] = np.mean(data['virtual_memory-percent'][-60:])
    
    return records