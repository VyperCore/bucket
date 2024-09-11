<!--
  ~ SPDX-License-Identifier: MIT
  ~ Copyright (c) 2023-2024 Vypercore. All Rights Reserved
  -->

## Adding coverage to the testbench

A sampler must be initialised with a reference to the top of the coverage hierarchy (the top level covergroup). The `sample()` method can then be passed a copy of the trace object each time, and will then recursively call each coverpoints sample method.

``` Python
    # My testbench

    cvg = MyBigCoverGroup(name="my_toplevel_covergroup", description="All of my coverage")

    sampler = MySampler(coverage=cvg)

    ...
    # Collect trace_data from monitors and other sources, then pass to coverage
    sampler.sample(trace_data)
```
---
### Sampler (optional)

If your trace information requires pre-processing, then you can override the Sampler's `process_trace()` method, which by default will just return the trace object unmodified.

For example:

``` Python
class MySampler(Sampler):
    def __init__(self, coverage):
        super().__init__(coverage=coverage)

    def process_trace(self, trace):
        ...
        # Modify trace object for all coverpoints
        ...
        return trace
```
---
<br>

Prev: [Filters](filters.md)
<br>
Next: [Export and merge](export_and_merge.md)
