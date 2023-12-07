class Sampler:
    """This class sample each coverpoint"""

    def __init__(self, coverage):
        self.coverage = coverage

        # Coverage should be instance of the coverage to be updated

    def sample(self, trace):
        """Go through the coverage tree and recursively call sample, passing in trace"""
        processed_trace = self.process_trace(trace)
        self.coverage.sample(processed_trace)

    def process_trace(self, trace):
        '''
        This function is to modify/preprocess the trace data into
        more useful for coverage. For now this will just return
        the trace as it is, but can be adapted as required.
        '''
        return trace