<!--
  ~ SPDX-License-Identifier: MIT
  ~ Copyright (c) 2023-2025 Vypercore. All Rights Reserved
  -->

## Adding coverage to the testbench

A sampler must be initialised with a reference to the top of the coverage hierarchy (the top level covergroup). The `sample()` method can then be passed a copy of the trace object each time, and will then recursively call each coverpoints sample method.

``` Python
    # My testbench

    cvg = MyBigCoverGroup(logger=self.log)

    ...
    # Collect trace_data from monitors and other sources, then pass to coverage
    cvg.sample(trace_data)
```
---
<br>

Prev: [Covertop](covertop.md)
<br>
Next: [Export and merge](export_and_merge.md)
