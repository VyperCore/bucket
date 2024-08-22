<!--
  ~ SPDX-License-Identifier: MIT
  ~ Copyright (c) 2023-2024 Vypercore. All Rights Reserved
  -->

# Getting Started:

```
$ ./bin/shell
$ python -m bucket.example
```

This page describes how to use Bucket to create coverpoints, sample data and merge results. Examples of coverpoints in use can be seen in [example.py](https://github.com/VyperCore/bucket/blob/main/bucket/example.py).

## Coverpoints

A coverpoint consists of one or more axes, which are then crossed. Each possible combination of the axes values is called a bucket. Each bucket has a default goal with a target of 10 hits, which can be modified as required, or can be made illegal or ignored.

Each new coverpoint should inherit from the Coverpoint class, and requires a 'name' and a 'description'.

``` Python
class MyCoverpoint(Coverpoint):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
```

A `setup()` method is then required to create the axes and goals of the coverpoint.

You use `add_axis()` to add each axis, which requires a name, description and some values.

| Parameter | Type | Description |
| --- | ---| ---|
| name | str | Should be machine readable, containing no spaces. It is suggested to use lower case |
| description | str | A short description of the coverpoint aim |
| values | dict,list,tuple,set | All the values/ranges to be covered by the axis |

`Values` can be in the form of numbers or strings. They are processed by the coverpoint when added. A name for each value/range will automatically be generated unless one is given. Names allow more meaning to be given to integers/ranges, while still allowing either the name or the value to be sampled. Names will be shown in the exported coverage.

To specify a named value, a dictionary should be used in the form `{'name': value}`. Alternatively, a list, tuple or set can be passed in and the names will be automatically created.
Ranges can also be specified by providing a MIN and MAX value in a list in place of a single value.<br>
eg. `[0,1,2,[3, 9], 10]`

The example below shows an axis being added with five buckets. Four of the buckets only accept a single value, while the remaining one can accept a value from `2` to `13`. Later, when sampling, either the auto-generated name of a bucket can be passed in (eg. "1", "2 -> 13", "15"), or the raw value can be passed instead (eg. 0, 5, 9)

``` Python
    def setup(self, ctx):
        self.add_axis(
            name="my_axis",
            values=[0, 1, [2, 13], 14, 15],
            description="Range of values for my_axis",
        )
```
### Tier and tags
If you wish to filter out coverpoints or allow for easier searching in the coverage viewer then you can set a tier and/or tags.
<b>
Tier: A coverpoints tier is set to 0 by default, which is the highest priority. Any value can be set. Later, the tier_level can be set by the testbench which will disable coverpoints of a lower priority tier.
<b>
Tags: Tags can be added to coverpoints to allow for easier filtering (where names may not make sense - such as a group coverpoints across several covergroups). They will also be made available in the coverage viewer so only coverpoints with matching tags are shown.

----

Goals can be optionally used to name buckets or to define ILLEGAL, IGNORE and modified hit counts. `add_goal` requires a name and a description. It can optionally include a new target hit count, or define the bucket(s) as ignore or illegal. If no target is provided, a default of 10 is currently used.

| Parameter | Type | Description |
| --- | --- | ---|
| name | str | Should be all caps, no spaces. It should also be uniquely named where possible |
| description | str | A short description of the goal aim |
| \[target\] | int | Target number of hits to saturate the bucket(s) |
| \[illegal\] | bool | Illegal. Bucket(s) will generate an error if hit |
| \[ignore\] | bool | Ignore. No coverage will be collected for the bucket(s) |

<br>
Each goal is created during setup(), normally after the axes have been defined. Below, one goal has been made ILLEGAL, while the other has increased the number of hits required to 20.

``` Python
        self.add_goal("MOULDY_CHEESE", "Not so gouda!", illegal=True)
        self.add_goal("OPTMISTIC_CHEESE", "I brie-live in myself!", target=20)
```

If goals have been created, then they must be applied to the relevant buckets. To do this the `apply_goals()` method must be overridden, which will be automatically called at the end of the setup phase. After filtering which buckets are to have a goal applied, the new goal should be returned. A default of 10 hits is otherwise applied.
NOTE: The **name** of the bucket is used, not the original value. For strings this should make no difference, but for values, you will need to convert them back to int. (Ranges will need to be referenced by name)

``` Python
    def apply_goals(self, bucket, goals):
        if bucket.my_axis_1 == "1" and bucket.my_axis_3 in ["red", "yellow"]:
            return goals.MOULDY_CHEESE
        elif int(bucket.my_axis_2) > 8:
            return goals.OPTMISTIC_CHEESE
```
---
<br>
Finally, a `sample()` method needs to be defined. This sets a bucket with a particular cross of axis values, which will have its hit count increased (if applicable).

A trace object can be of any type, but is intended to be a class containing all information to be covered (from a monitor, model, etc). Each coverpoint can then sample the relevant information. This could be as simple as directly assigning values to each axis, processing the values into something more useful and/or storing values for the next time the coverpoint is called.

`set_axes()` is used to assign each axis a value/named-value. (eg. If the values `[0,1,2]` were given the names `[red,green,blue]` then either `0` or `red` could be assigned to the bucket). Once all axes have been set, then the bucket hit count can be incremented. If it is a regular bucket, then the hit count will be increased. If it is an IGNORE bucket, no action will be taken, and if it is an ILLEGAL bucket an error will be generated.

> **NOTE: The bucket should have every axis of the coverpoint assigned a valid value when hit() is called. Attempting to sample while not setting the bucket correctly will result in an error. (This is because the hit() function won't know which exact combination of axis values to count as hit).**

If multiple values are to be sampled for a given call of a coverpoint, then all axis values of the bucket do not need to be re-set. Only the ones which have changed need to be overridden with new values.

``` Python
    def sample(self, trace):
        # 'with bucket' is used, so bucket values are cleared each time.
        # bucket can also be manaually cleared by using bucket.clear()
        with self.bucket as bucket:
            bucket.set_axes(
                my_axis_1=trace.monitor_a.interface_b.signal,
                my_axis_2=trace.instruction.operand.type,
            )

            # For when multiple values might need covering from one trace
            # Only need to re-set the axes that change
            for gpr in range(len(trace.registers_accessed)):
                bucket.set_axes(my_axis_3=trace.registers[gpr])
                bucket.hit()
```
---
<br>

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
<br>

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

## Filtering coverage

### Filtering by function

Coverpoint and Covergroups may be filtered to allow coverage to run quicker. This is useful when working on a small subset of coverage and you don't want to run everything, or for follow-up regressions to exclude already saturated coverpoints. Below are the methods to include, restrict or exclude coverage which match the condition provided.

| Function  | Description |
|---|---|
| `include_by_function()` | Enable coverpoints which match. Unmatched coverpoints will not have their active state changed, except this is the first filter to be applied, then any coverpoints which do not match are explicitly set to inactive, as the default state is active. |
| `restrict_by_function()` | Restrict to coverpoints which match. Matched coverpoints will not change state. Unmatched will be disabled |
| `exclude_by_function()` |  Disable coverpoints which match. Unmatched coverpoints will not change state |

| Parameter | Type | Description |
| --- | --- | ---|
| matcher | Callable | A function to match against coverpoints/covergroups. Expect a True/False result |
| cp_only | bool | Should function match against coverpoints only, or both coverpoints and covergroups? |

Eg. `cp_only` can be set False when filtering against names to be able to match against a covergroup and enable all coverpoints it contains. However, you may want it set to match against coverpoints only when filtering with tags, as covergroups will accumulate all of their children's tags.


Some additional helper functions have been provided to allow for easy use of common use-cases. You are able mix these with your own match functions as required.

| Functions | Description |
|---|---|
| `*_by_name` | Provide a list of names to match against |
| `*_by_tag` | Provide a list of tags to match against (either match all or some) |

NOTE: The filters stack in the order they are provided. It is recommended that they are applied in the order of include -> restrict -> exclude, but you are able to layer them in any order you like.

### Set tier level

| Functions | Description |
|---|---|
| `set_tier_level` | Restrict coverpoints to the requested tier level. Lower values are higher priority |

All coverpoints default to tier 0 if they aren't explicitly set and will be enabled by default. This sets the tier level separately to the filter functions. If you want to use `tier` as part of your match criteria you are able to do so with `*_by_function()`.


```
    # Only run branch related coverage which are tier 1 or lower.
    cvg = MyBigCoverGroup(name="my_toplevel_covergroup", description="All of my coverage")
    cvg.include_by_name('branch_coverage')
    cvg.set_tier_level(1)
```
The strings/values are hardcoded in the example above, but are intended to come from command line arguments/input files/etc.


## Exporting coverage

At the end of each testcase, it is possible to export the coverage data to SQL. This can be stored locally, or fed directly into a database hosted elsewhere.

Coverage merging can also be performed at the end of a regression to combine all test case data.
