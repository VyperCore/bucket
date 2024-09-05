<!--
  ~ SPDX-License-Identifier: MIT
  ~ Copyright (c) 2023-2024 Vypercore. All Rights Reserved
  -->

## Covergroups

Covergroups are a way to provide hierarchy by grouping coverpoints and other covergroups. A `print_tree()` function can be called to display how covergroups/coverpoints are organised.

Each covergroup should inherit from the Covergroup class, and requires a 'name' and 'description'

``` Python
class MyBigCoverGroup(Covergroup):
    def setup(self, ctx):
        self.add_covergroup(
            MyCovergroup(name="my_covergroup", description="A group of coverpoints")
        )
        self.add_coverpoint(MyCoverpoint(name="some_coverpoint", description="A coverpoint"))
```
---
### Tier and tags
If you wish to filter out coverpoints or allow for easier searching in the coverage viewer then you can set a tier and/or tags. These are applied to a coverpoint instance within the covergroup setup phase.
<br>

`Tier`: A coverpoints tier is set to 0 by default, which is the highest priority. Any value can be set. Later, the tier_level can be set by the testbench which will disable coverpoints of a lower priority tier.
<br>

`Tags`: Tags can be added to coverpoints to allow for easier filtering (where names may not make sense - such as a group of coverpoints across several covergroups). They will also be made available in the coverage viewer so only coverpoints with matching tags are shown.


---
<br>

Prev: [Coverpoints](coverpoints.md)
<br>
Next: [Sampler](sampler.md)
