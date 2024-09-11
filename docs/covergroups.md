<!--
  ~ SPDX-License-Identifier: MIT
  ~ Copyright (c) 2023-2024 Vypercore. All Rights Reserved
  -->

## Covergroups

Covergroups are a way to provide hierarchy by grouping coverpoints and other covergroups. A `print_tree()` function can be called to display how covergroups/coverpoints are organised.

Each covergroup should inherit from the Covergroup class. When instancing, each coverpoint can optionally be passed a 'name' and a 'description' to override the defaults. There is no need to override the `__init__` method if you are setting these fields within the covergroup, or overriding them when instancing. Covergroups can contain coverpoints as well as other covergroups. They are added during the `setup()` phase using the `add_coverpoint` and `add_covergroup` functions.

``` Python
class MyBigCoverGroup(Covergroup):
    NAME = "default_covergroup_name"
    DESCRIPTION = "Default description goes here"

    def setup(self, ctx):
        self.add_covergroup(
            # Here we demonstrate overriding the default name and description of a covergroup
            MyCovergroup(name="my_covergroup", description="A group of coverpoints")
        )
        self.add_coverpoint(
            MyCoverpoint()
            .set_tier(1)
            .set_tags(["tag_a", "tag_b"])
        )
```
As seen above, there are methods for overriding or adding to the tier and tags when instancing a coverpoint.

|Method| parameter|description|
|--|--|--|
|set_tier| `int`| Override the default `tier` for this instance|
|set_tags| `list[str]` or `str` |  Override the default `tags` for this instance|
|add_tags| `list[str]` or `str` |  Add to the default `tags` for this instance|

---
### Smart Sampling
If a covergroup is known to contain coverpoints/covergroups which will only cover a subset of data, then the user can optionally provide a `should_sample` function. This will prevent any sampling in any sub-coverpoints/covergroups when the data would not be sampled.
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
