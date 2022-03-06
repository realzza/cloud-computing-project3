import numpy as np
from typing import Dict, Any

    
def handler(data: dict, context: object) -> Dict[str, Any]:
    
    records = {}
    cpu_env = {}
    # for the first time, env will be initialized, afterwards it can be directly retrieved and updated
    # try:
    if getattr(context.env, "cpu_buffer", None) is None:
        n_cpus = 0
        context.env["stream_data"] = {}
        for i in range(100):
            if not "cpu_percent-%d"%i in data:
                break
            n_cpus += 1
            context.env["stream_data"][i] = [0]*720
        
        # init VM usage
        context.env["vm_usage"] = [0]*60
        assert n_cpus > 0, "problematic data stream stored in redis. Please contract maintainer for assistance"
        
        cpu_env['n_cpus'] = n_cpus
        context.env['cpu_buffer'] = cpu_env

    cpu_env = context.env['cpu_buffer']
    n_cpus = cpu_env['n_cpus']

    for i in range(n_cpus):
        curr_data = data['cpu_percent-%d'%i]
        context.env['stream_data'][i].append(curr_data)
        curr_stream = context.env['stream_data'][i][::-1][:720]
        # print(curr_data)
        records['cpu_%d_1min_avg'%i] = np.mean(curr_stream[:12])
        cpu_env['cpu_%d_1min_avg'%i] = np.mean(curr_stream[:12])
        records['cpu_%d_1h_avg'%i] = np.mean(curr_stream[:720])
        cpu_env['cpu_%d_1h_avg'%i] = np.mean(curr_stream[:720])

    context.env["vm_usage"].append(data['virtual_memory-percent'])
    records['VM_used_past_5min_avg'] = np.mean(context.env['vm_usage'][::-1][:60])
    # records = {k: str(v) for k,v in records.item()}
    # except Exception as e:
    #     records["error"] = str(e)
    
    return records