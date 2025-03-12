import math
import os
import numpy as np

''' Cntains all possible metrics that are computed for Hab1, Hab2, 5 CSR, CPT'''

def correct_perc(correct, incorrect):
    if(correct==0 and incorrect==0):
        return 0
    return correct/(correct+incorrect) * 100

def omission_perc(omission, correct, incorrect):
    if(correct==0 and omission==0 and incorrect==0):
        return 0
    return omission/(correct+incorrect+omission) * 100

def c_wh_perc(c_wh, i_wh):
    if(i_wh==0 and c_wh==0):
        return 0
    return c_wh/(c_wh+i_wh) * 100

def diff_wh(c_wh_perc, om_perc):
    '''diff between %c_wh and %omission'''
    return c_wh_perc - om_perc

def false_alarm(c_wh, i_wh):
    if(i_wh==0 and c_wh==0):
        return 0
    return i_wh/(c_wh+i_wh) * 100

def hit_rate(correct, incorrect, omission):
    if(correct==0 and omission==0 and incorrect==0):
        return 0
    return correct/(correct+incorrect+omission) * 100

def sensitivity_index():
    raise NotImplementedError
    
def responsivity_index():
    raise NotImplementedError

def compute_threshold(task, metrics):
    if task == "hab1":
        '''Requires 30 or more responses within 2 days'''
        if(metrics["Count"] >= 30):
            return True
        else:
            return False
        
    elif task == "hab2":
        '''Requires 70 or more responses within 2 days'''
        if((metrics["Count"] >= 70)):
            return True
        else:
            return False
        
    elif task == "5csr_citi_10":
        '''30 correct respones + MCL of less than half of stim duration'''
        if(metrics["Correct"] >= 30) & (metrics["Mean Correct Latency"] < 5000):
            return True
        else:
            return False
    

    elif task == "5csr_citi_8":
        '''30 correct respones + MCL of less than half of stim duration'''
        if(metrics["Correct"] >= 30) & (metrics["Mean Correct Latency"] < 4000):
            return True
        else:
            return False
    
    elif task == "5csr_citi_4":
        '''30 correct respones + MCL of less than half of stim duration'''
        if(metrics["Correct"] >= 30) & (metrics["Mean Correct Latency"] < 2000):
            return True
        else:
            return False
    
    elif task == "5csr_citi_2" or "5csr_viti":
        '''30 correct respones + MCL of less than half of stim duration'''
        if(metrics["Correct"] >= 30) & (metrics["Mean Correct Latency"] < 1500):
            return True
        else:
            return False
    
    elif task == "rcpt_viti_2_to_1":
        '''30 correct respones + MCL of less than half of stim duration'''
        if(metrics["Count"] >= 30) & (metrics["Mean Correct Latency"] < 1500):
            return True
        else:
            return False
        
    elif task == "rcpt_viti_2":
        '''30 correct respones + MCL of less than half of stim duration'''
        if(metrics["Count"] >= 30) & (metrics["Mean Correct Latency"] < 1500):
            return True
        else:
            return False
    
    elif task == "rcpt_viti_175":
        '''30 correct respones + MCL of less than half of stim duration'''
        if(metrics["Count"] >= 30) & (metrics["Mean Correct Latency"] < 1500):
            return True
        else:
            return False
    
    elif task == "rcpt_viti_15":
        '''30 correct respones + MCL of less than half of stim duration'''
        if(metrics["Count"] >= 30) & (metrics["Mean Correct Latency"] < 1500):
            return True
        else:
            return False