<!--
  ~ SPDX-License-Identifier: MIT
  ~ Copyright (c) 2023-2024 Vypercore. All Rights Reserved
  -->

## Sampler (optional)

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

Prev: [Covergroups](covergroups.md)
<br>
Next: [Adding coverage to the testbench](add_to_testbench.md)
