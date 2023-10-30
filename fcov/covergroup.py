class Covergroup:
    """This class groups coverpoints together, and adds them to the hierarchy"""

    def __init__(self, name, description):
        """
        Parameters:
            name: Name of covergroup
            description: Description of covergroup
            cvg_tier: what coverage tier is being run [0..3]
        """

        self.name = name
        self.description = description

        self.coverpoints = {}
        self.covergroups = {}
        self.setup()

    def add_coverpoint(self, coverpoint):
        """
        Add a coverpoint instance to the covergroup
        Parameters:
            coverpoint: instance of a coverpoint
            trigger:    [optional] specific trigger on which to sample the coverpoint
        """
        if coverpoint.name in self.coverpoints:
            raise Exception("Coverpoint names must be unique within a covergroup")

        self.coverpoints[coverpoint.name] = coverpoint
        setattr(self, coverpoint.name, coverpoint)

    def add_covergroup(self, covergroup):
        """
        Add a covergroup instance to the covergroup
        Parameters:
            covergroup: instance of a covergroup
        """
        if covergroup.name in self.covergroups:
            raise Exception("Covergroup names must be unique within a covergroup")

        self.covergroups[covergroup.name] = covergroup
        setattr(self, covergroup.name, covergroup)

    def setup(self):
        raise NotImplementedError("This needs to be implemented by the coverpoint")

    def print_tree(self, indent=0):
        """Print out coverage hierarch from this covergroup down"""
        if indent == 0:
            print("COVERAGE_TREE")
            print(f"* {self.name}: {self.description}")
        indent += 1
        indentation = "    " * indent
        for cp in self.coverpoints.values():
            print(f"{indentation}|-- {cp.name}: {cp.description}")

        for cg in self.covergroups.values():
            print(f"{indentation}|-- {cg.name}: {cg.description}")
            cg.print_tree(indent + 1)

    def sample(self, trace):
        """Call sample on all sub-groups and coverpoints, passing in trace"""
        for cp in self.coverpoints.values():
            cp.sample(trace)

        for cg in self.covergroups.values():
            cg.sample(trace)

    def export_coverage(self):
        for cp in self.coverpoints.values():
            print(f'Exporting coverage for "{cp.name}"')
            cp.export_coverage()

        for cg in self.covergroups.values():
            cg.export_coverage()