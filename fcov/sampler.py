class Sampler:
    """This class sample each coverpoint"""

    def __init__(self, coverage):
        self.coverage = coverage

        # Coverage should be instance of the coverage to be updated

    def sample(self):
        """Go through the coverage tree and recursively call sample, passing in trace"""
        trace = self.create_trace()
        self.coverage.sample(trace)

    def create_trace(self):
        """Take in all relevent information and put into a structure (eg. dataClass)"""
        raise NotImplementedError("This needs to be implemented by the testbench")