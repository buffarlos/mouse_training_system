import math
import os
import numpy as np

''' Cntains all possible metrics that are computed for Hab1, Hab2, 5 CSR, CPT'''

def correct_perc(correct, incorrect):
    return correct/(correct+incorrect)

def omission_perc(omission, correct, incorrect):
    return omission/(correct+incorrect+omission)

def c_wh_perc(c_wh, i_wh):
    return c_wh/(c_wh+i_wh)

def diff_wh(c_wh_perc, om_perc):
    '''diff between %c_wh and %omission'''
    return c_wh_perc - om_perc

def false_alarm(c_wh, i_wh):
    return i_wh/(c_wh+i_wh)

def hit_rate(correct, incorrect, omission):
    return correct/(correct+incorrect+omission)

def sensitivity_index():
    raise NotImplementedError
    
def responsivity_index():
    raise NotImplementedError

def compute_threshold(task, metrics):
    if task == "hab1":
        '''Requires 30 or more responses within 2 days'''
        if(metrics["Correct"] + metrics["Incorrect"] >= 30):
            return True
        else:
            return False
        
    elif task == "hab2":
        '''Requires 70 or more correct responses within 2 days'''
        if(metrics["Correct"] >= 70):
            return True
        else:
            return False
        
    elif task == "5csr":
        raise NotImplementedError
    
    elif task == "cpt":
        raise NotImplementedError
    
    else:
        raise NotImplementedError