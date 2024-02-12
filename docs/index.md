# Getting Started:

```
$ poetry install
$ poetry shell
$ python -m bucket.example
```

This page describes how to use Bucket to create coverpoints, sample data and merge results. Examples of coverpoints in use can be seen in `example.py`.

## Coverpoints

A coverpoint consists of one or more axes, which are then crossed. Each possible combination of the axes values is called a bucket. Each bucket has a default goal with a target of 10 hits, which can be modified as required, or can be made illegal or ignored. 

Each new coverpoint should inherit from the Coverpoint class, and requires a 'name' and a 'description'. 

``` Python
class MyCoverpoint(Coverpoint):
    def __init__(self, name: str, description: str, trigger=None):
        super().__init__(name, description, trigger=None)
```

A `setup()` method is then required to create the axes and goals of the coverpoint. This function will only be called if the coverpoint is active. Next, you use `add_axis()` which requires a name, description and values.

| Parameter | Type | Description |
| --- | ---| ---|
| name | str | Should be machine readable, containing no spaces. It is suggested to use lower case |
| description | str | A short description of the coverpoint aim |
| values | dict,list,tuple,set | All the values/ranges to be covered by the axis |

`Values` can be in the form of numbers or strings. They are processed by the coverpoint when added. A name for each value/range will automatically be generated unless one is given. Names allow more meaning to be given to integers/ranges, while still allowing either the name or the value to be sampled. Names will be shown in the exported coverage.

To specify a named value, a dictionary should be used in the form `{'name': value}`. 
Alternatively, a list, tuple or set can be passed in and the names will be automatically created.
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

----

Goals can be optionally used to name buckets or to define ILLEGAL, IGNORE and modified hit counts. `add_goal` requires a name, target hit count and a description.

| Parameter | Type | Description |
| --- | --- | ---|
| name | str | Should be all caps, no spaces. It should also be uniquely named where possible |
| hits | int | Target number of hits to saturate the bucket(s). Some special values are accepted (See below)|
| description | str | A short description of the goal aim |
<br>

`ILLEGAL` and `IGNORE` goals can be configured by using special values. 
| Value | Descrpition |
| --- | --- |
| 1+ | Target number of hits to saturate the bucket(s) |
| 0 | Ignore. No coverage will be collected for the bucket(s) |
| -1 | Illegal. Bucket(s) will generate an error if hit |

<br>
Each goal is created during setup(), normally after the axes have been defined. Below, one goal has been made ILLEGAL, while the other has increased the number of hits required to 20.

``` Python
        self.add_goal("MOULDY_CHEESE", -1, "Not so gouda!")
        self.add_goal("OPTMISTIC_CHEESE", 20, "I brie-live in myself!")
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
Finally, a `sample()` method needs to be defined. This uses a cursor to point to a particular cross of axis values, which will have its hit count increased (if applicable).

A trace object can be of any type, but is intended to be a class containing all information to be covered (from a monitor, model, etc). Each coverpoint can then sample the relevant information. This could be as simple as directly assigning values to each axis, processing the values into something more useful and/or storing values for the next time the coverpoint is called. 

To set each axis, `set_cursor()` is used, with each axis name being assigned a value/named-value. (eg. If the values `[0,1,2]` were given the names `[red,green,blue]` then either `0` or `red` could be assigned to the cursor). Once all axes have been set, then the cursor can be incremented. If it is a regular bucket, then the hit count will be increased. If it is an IGNORE bucket, no action will be taken, and if it is an ILLEGAL bucket an error will be generated. 

> **NOTE: The cursor should have every axis of the coverpoint set to a valid value when increment is called. Attempting to sample while not setting the cursor correctly will result in an error. (This is because the increment function won't know which exact cross of axis values to count as hit).**

If multiple values are to be sampled for a given call of a coverpoint, then all axes of the cursor do not need to be re-set. Only the ones which have changed need to be overridden with new values.

``` Python
    def sample(self, trace):
        # 'with cursor' is used, so cursor values are cleared each time.
        # cursor can also be manaually cleared by using cursor.clear()
        with self.cursor as cursor:
            cursor.set_cursor(
                my_axis_1=trace.monitor_a.interface_b.signal,
                my_axis_2=trace.instruction.operand.type,
            )

            # For when multiple values might need covering from one trace
            # Only need to re-set the axes that change
            for gpr in range(len(trace.registers_accessed)):
                cursor.set_cursor(my_axis_3=trace.registers[gpr])
                cursor.increment()
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

A sampler must be initialised with a reference to the top of the coverage heierarchy (the top level covergroup). The `sample()` method can then be passed a copy of the trace object each time, and will then recursively call each coverpoints sample method. 

``` Python
    # My testbench

    cvg = MyBigCoverGroup(name="my_toplevel_covergroup", description="All of my coverage")

    sampler = MySampler(coverage=cvg)

    ...
    # Collect trace_data from monitors and other sources, then pass to coverage
    sampler.sample(trace_data)
```


## Exporting coverage

At the end of each testcase, it is possible to export the coverage data to SQL. This can be stored locally, or fed directly into a database hosted elsewhere. 

Coverage merging can also be performed at the end of a regression to combine all test case data.
