<!--
  ~ SPDX-License-Identifier: MIT
  ~ Copyright (c) 2023-2024 Vypercore. All Rights Reserved
  -->

## Exporting coverage


It is possible to export the coverage data to SQL. This can be stored locally, or fed directly into a database hosted elsewhere. Coverage merging can also be performed to combine all coverage data from multiple simulations.


At the end of a simulation, the recorded coverage should be exported for later reading/processing.

```Python
    # In your testbench
    self.my_cvg = MyCvg(name="my_cvg", description="All my coverage")

    def export_coverage(self):
        # Create a context specific hash
        # This is stored alongside recorded coverage and is used to determine if coverage is valid to merge.
        context_hash = Repo().head.object.hexsha

        # Collect coverage
        reading = PointReader(context_hash).read(self.my_cvg)

        # Write summary out to console
        ConsoleWriter(axes=False, goals=False, points=False, summary=True).write(reading)

        # Write out to file
        SQLAccessor.File("cvg.db").write(reading)

```

## Merging coverage

After running a regression, coverage from the separate simulations should be merged together ready to be viewed.

At present a simple merge is done, with the merged dataset being produced. In future we plan to support producing a golden testset which will contain the subset of tests required to hit the same coverage. We also plan to provide more detailed analysis as to which buckets were hit by which testcases.

To merge coverage, the following commands should be run as part of your simulation/regression script:

```Python
    # Do some code here
```
---
<br>

Prev: [Adding coverage to the testbench](add_to_testbench.md)
<br>
Next: [Viewing coverage](viewing_coverage.md)
