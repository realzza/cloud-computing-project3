import numpy as np
from typing import Dict, Any

    
def handler(data: dict, context: object) -> Dict[str, Any]:
    
    records = {}
    cpu_env = {}
    # for the first time, env will be initialized, afterwards it can be directly retrieved and updated
    # try:
    if getattr(context.env, "cpu_buffer", None) is None:
        n_cpus = 0
        context.env["ewma"] = {"min":{},"hour":{}}
        for i in range(100):
            if not "cpu_percent-%d"%i in data:
                break
            n_cpus += 1
            context.env["ewma"]["min"][i] = 0
            context.env["ewma"]["hour"][i] = 0
        
        # init VM usage
        context.env["ewma"]["vm_usage"] = 0
        assert n_cpus > 0, "problematic data stream stored in redis. Please contract maintainer for assistance"
        
        cpu_env['n_cpus'] = n_cpus
        context.env['cpu_buffer'] = cpu_env

    cpu_env = context.env['cpu_buffer']
    n_cpus = cpu_env['n_cpus']
    ewma_buffer = context.env['ewma']

    records['time'] = data['timestamp']
    # 1/(1-beta) = days of avg
    beta_m = 11/12     # mean for 12 data points, which is one minute
    beta_h = 719/720   # mean for 720 datapoints, which is ont hour
    beta_vm = 59/60
    for i in range(n_cpus):
        curr_data = data['cpu_percent-%d'%i]
        records['cpu_%d_1min_ewma'%i] = round(curr_data*beta_m + (1-beta_m)*ewma_buffer['min'][i],4)
        ewma_buffer['min'][i] = curr_data*beta_m + (1-beta_m)*ewma_buffer['min'][i]
        records['cpu_%d_1h_ewma'%i] = round(curr_data*beta_h + (1-beta_h)*ewma_buffer['hour'][i],4)
        ewma_buffer['hour'][i] = curr_data*beta_h + (1-beta_h)*ewma_buffer['hour'][i]

    vm_usage_curr = data['virtual_memory-percent']
    records['VM_used_past_5min_avg'] = round(vm_usage_curr*beta_vm + ewma_buffer["vm_usage"]*(1-beta_vm),4)
    ewma_buffer["vm_usage"] = vm_usage_curr*beta_vm + ewma_buffer["vm_usage"]*(1-beta_vm)
    
    return records