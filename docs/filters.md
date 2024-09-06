
<!--
  ~ SPDX-License-Identifier: MIT
  ~ Copyright (c) 2023-2024 Vypercore. All Rights Reserved
  -->

## Filtering coverage

### Filtering by function

Coverpoint and Covergroups may be filtered to allow coverage to run quicker. This is useful when working on a small subset of coverage and you don't want to run everything, or for follow-up regressions to exclude already saturated coverpoints. Below are the methods to include, restrict or exclude coverage which match the condition provided.

| Function  | Description |
|---|---|
| `include_by_function()` | Enable coverpoints which match. Unmatched coverpoints will not have their active state changed, except when this is the first filter to be applied, then any coverpoints which do not match are explicitly set to inactive, as the default state is active. |
| `restrict_by_function()` | Restrict to coverpoints which match. Matched coverpoints will not change state. Unmatched will be disabled |
| `exclude_by_function()` |  Disable coverpoints which match. Unmatched coverpoints will not change state |

| Parameter | Type | Description |
| --- | --- | ---|
| matcher | Callable | A function to match against coverpoints/covergroups. Expect a True/False result |

Some additional helper functions have been provided to allow for easy use of common use-cases. You are able mix these with your own match functions as required.

| Functions | Description |
|---|---|
| `include_by_name`<br>`restrict_by_name`<br>`exclude_by_name` | Provide a list of names to match against both coverpoints and covergroups|
| `include_by_tag`<br>`restrict_by_tag`<br>`exclude_by_tag` | Provide a list of tags to match against (either match all or some). Coverpoints only|

When filtering by name, both covergroups and coverpoints are matched so you can enable all children of a covergroup easily. However, filtering by tag only matches against coverpoints, as covergroups will accumulate all of their children's tags and may match unexpectedly.

NOTE: The filters stack in the order they are provided. It is recommended that they are applied in the order of include -> restrict -> exclude, but you are able to layer them in any order you like.

### Set tier level

| Functions | Description |
|---|---|
| `set_tier_level` | Restrict coverpoints to the requested tier level and below. Lower values are higher priority |

All coverpoints default to tier 0 if they aren't explicitly set and will be enabled by default. This sets the tier level separately to the filter functions. If you want to use `tier` as part of your match criteria you are able to do so with `*_by_function()`.


```
    # Only run branch related coverage which are tier 1 or lower.
    cvg = MyBigCoverGroup(name="my_toplevel_covergroup", description="All of my coverage")
    cvg.include_by_name('branch_coverage')
    cvg.set_tier_level(1)
```
NOTE: The strings/values are hardcoded in the example above, but are intended to come from command line arguments/input files/etc.

---
<br>

Prev: [Covergroups](covergroups.md)
<br>
Next: [Adding coverage to the testbench](add_to_testbench.md)
