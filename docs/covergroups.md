<!--
  ~ SPDX-License-Identifier: MIT
  ~ Copyright (c) 2023-2024 Vypercore. All Rights Reserved
  -->

## Covergroups

Covergroups are a way to provide hierarchy by grouping coverpoints and other covergroups. A `print_tree()` function can be called to display how covergroups/coverpoints are organised.

Each covergroup should inherit from the Covergroup class, and requires a 'name' and 'description'. Covergroups can contain coverpoints as well as other covergroups. They are added during the `setup()` phase using the `add_coverpoint` and `add_covergroup` functions.

``` Python
class MyBigCoverGroup(Covergroup):
    def setup(self, ctx):
        self.add_covergroup(
            MyCovergroup(name="my_covergroup", description="A group of coverpoints")
        )
        self.add_coverpoint(
            MyCoverpoint(name="some_coverpoint", description="A coverpoint")
            .set_tier(1)
            .set_tags(["tag_a", "tag_b"])
        )
```
---
### Tier and tags
If you wish to filter coverpoints or allow for easier searching in the coverage viewer then you can set a tier and/or tags per coverpoint instance. These are optionally applied to each within the covergroup setup phase.
<br>

`Tier`: A coverpoint's tier is set to 0 by default, which is the highest priority. Any value can be set. When running a simulation, the tier_level can be set by the testbench which will disable coverpoints of a lower priority tier.
<br>

`Tags`: Tags can be added to coverpoints to allow for easier filtering (where relying names may not make sense - such as a group of coverpoints across several covergroups). They will also be made available in the coverage viewer so only coverpoints with matching tags are shown.

---
### Smart Sampling
If the covergroup is known to only contain coverpoints/covergroups which will only cover a subset of data, then the user can optionally provide a `should_sample` function. This will prevent any sampling in any sub-coverpoints/covergroups.
```Python
    def should_sample(self, trace):
        """
        This function is used to stop coverpoints being called when not relevant
        """
        return True if trace["type"] == "Dog" else False
```

---
<br>

Prev: [Coverpoints](coverpoints.md)
<br>
Next: [Filters](filters.md)
