# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Vypercore. All Rights Reserved

class Sampler:
    '''
    This class takes a reference to the top of of the coverage tree
    - process_trace() can be overridden if trace data needs modifying before covering.
    - sample() calls sample in each active covergroup/coverpoint
    '''

    def __init__(self, coverage):
        # Coverage should be instance of the coverage to be updated
        self.coverage = coverage

    def sample(self, trace):
        '''Go through the coverage tree and recursively call sample, passing in trace'''
        processed_trace = self.process_trace(trace)
        self.coverage.sample(processed_trace)

    def process_trace(self, trace):
        '''
        This function is to modify/preprocess the trace data into
        more useful for coverage. For now this will just return
        the trace as it is, but can be adapted as required.
        '''
        return trace