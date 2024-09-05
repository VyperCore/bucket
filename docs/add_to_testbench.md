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
<br>
Prev: [Sampler](sampler.md)
Next: [Filters](filters.md)
