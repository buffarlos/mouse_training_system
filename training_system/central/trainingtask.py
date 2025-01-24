import math
import os
import numpy as np

'''Implementation of training tasks.
Assumptions:
1. All metrics are reset if mice goes onto next stage (after being saved)
2. 

'''
class TrainingTask(object):
    def __init__(self, task, metrics):
        self.task = task
        self.metrics = metrics

    def compute_threshold(self):
        if self.task == "hab1":
            '''Requires 30 or more responses within 2 days'''

        elif self.task == "hab2":
            '''Requires 70 or more correct responses within 2 days'''

        elif self.task == "5csr":
            raise NotImplementedError
        
        elif self.task == "cpt":
            raise NotImplementedError
        
        else:
            raise NotImplementedError