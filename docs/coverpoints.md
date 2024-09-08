<!--
  ~ SPDX-License-Identifier: MIT
  ~ Copyright (c) 2023-2024 Vypercore. All Rights Reserved
  -->

## Coverpoints

A coverpoint consists of one or more axes, which are then crossed. (An axis covers one signal/data - similar to a UVM coverpoint). Each possible combination of the axes' values is called a bucket. Each bucket has a default goal with a target of 10 hits, which can be modified as required, or can be made illegal or ignored.

Each new coverpoint should inherit from the Coverpoint class, and requires a 'name' and a 'description'. More arguments can be passed to the coverpoint as required (see example files).

``` Python
class MyCoverpoint(Coverpoint):
```
---
A `setup()` method is then required to add the axes and goals of the coverpoint.

You use `add_axis()` to add each axis, which requires a name, description and some values.

| Parameter | Type | Description |
| --- | ---| ---|
| name | str | Should be machine readable, containing no spaces. It is suggested to use lower case |
| description | str | A short description of the coverpoint aim |
| values | dict,list,tuple,set | All the values/ranges to be covered by the axis |

`Values` can be in the form of numbers or strings. They are processed by the coverpoint when added. A name for each value/range will automatically be generated unless one is given. Names allow more meaning to be given to numbers/ranges, while still allowing either the name or the value to be sampled. Names will be shown in the exported coverage.

To specify a named value, a dictionary should be used in the form `{'name': value}`. Alternatively, a list, tuple or set can be passed in and the names will be automatically created.
<br>

Ranges can also be specified by providing a MIN and MAX value in a list in place of a single value.<br>
Eg. `[0, 1, 2, [3, 9], 10]`

The example below shows an axis being added with five buckets. Four of the buckets only accept a single value, while the remaining one can accept any value from `2` to `13`. Later, when sampling, either the auto-generated name of a bucket can be passed in (eg. "1", "2 -> 13", "15"), or the raw value can be passed instead (eg. 0, 5, 9)

``` Python
    def setup(self, ctx):
        self.add_axis(
            name="my_axis",
            values=[0, 1, [2, 13], 14, 15],
            description="Range of values for my_axis",
        )
```
----

### Goals
Goals can be optionally used to name buckets or to define ILLEGAL, IGNORE and modified hit counts. `add_goal` requires a name and a description. It can optionally include a new target hit count, or define the bucket(s) as ignore or illegal. If no target is provided, a default of 10 is currently used. Only one of `target`, `illegal` and `ignore` can be set for a given goal.

| Parameter | Type | Description |
| --- | --- | ---|
| name | str | Should be all caps, no spaces. It should also be uniquely named where possible |
| description | str | A short description of the goal aim |
| \[target\] | int | Target number of hits to saturate the bucket(s) |
| \[illegal\] | bool | Illegal. Bucket(s) will generate an error if hit |
| \[ignore\] | bool | Ignore. No coverage will be collected for the bucket(s) |

<br>
Each goal is created during setup(), normally after the axes have been defined. Below, one goal has been made ILLEGAL, while the other has increased the number of hits required to 20.

<br>

``` Python
        self.add_goal("MOULDY_CHEESE", "Not so gouda!", illegal=True)
        self.add_goal("OPTMISTIC_CHEESE", "I brie-live in myself!", target=20)
```

If goals have been created, then they must be applied to the relevant buckets. To do this the `apply_goals()` method must be overridden, which will be automatically called at the end of the setup phase. After filtering which buckets are to have a goal applied, the new goal should be returned. A default of 10 hits is otherwise applied.
<br>

NOTE: The **name** of the axis value is used, not the original value. For strings this should make no difference, but for values, you will need to convert them back to int/float/etc. (Ranges will need to be referenced by name. However setting all ranges to a goal could match against "->" for example).

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

<br>

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
### Passing the coverpoint extra arguments

If you wish to create a coverpoint which relies on other data (such as a pre-processed list of instruction names, etc), then further arguments can be provided. These should all be placed before `super().__init_()` if you want them to be accessible to the `setup()` method.

The example below shows instancing the same coverpoint twice with different names. These extra parameters could come from automatically generated lists which split up the original data into smaller groups.
```Python
class ChewToysByName(Coverpoint):
    def __init__(self, name: str, description: str, names):
        self.name_group = names
        super().__init__(name, description)

    def setup(self, ctx):
        self.add_axis(
            name="name",
            values=self.name_group,
            description="Most important dog names only",
        )
...
# To be instanced as below:
class DogsAndToys(Covergroup):
    def setup(self, ctx):
        self.add_coverpoint(
            ChewToysByName(
                name="chew_toys_by_name__group_a",
                description="Preferred chew toys by name (Group A)",
                names=["Barbara", "Connie", "Graham"],
            )
        )
        self.add_coverpoint(
            ChewToysByName(
                name="chew_toys_by_name__group_b",
                description="Preferred chew toys by name (Group B)",
                names=["Clive", "Derek", "Ethel"],
            )
        )
```


---
<br>

Prev: [Index](index.md)
<br>
Next: [Covergroups](covergroups.md)
