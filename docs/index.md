<!--
  ~ SPDX-License-Identifier: MIT
  ~ Copyright (c) 2023-2024 Vypercore. All Rights Reserved
  -->

# Getting Started:

To run the example, which includes a coverage tree along with some randomised data to sample, please run:

```
$ ./bin/shell
$ python -m example.example
```

Below describes how to use Bucket to create coverpoints, sample your data and then merge the results. Examples of coverpoints in use can be seen in [cats.py](https://github.com/VyperCore/bucket/blob/main/example/cats.py) and [dogs.py](https://github.com/VyperCore/bucket/blob/main/example/dogs.py).

# Contents
1. [Coverpoints](coverpoints.md)
2. [Covergroups](covergroups.md)
3. [Filters](filters.md)
4. [Adding coverage to the testbench](add_to_testbench.md)
5. [Merging coverage](merging_coverage.md)
6. [Viewing coverage](viewing_coverage.md)





## Exporting coverage

At the end of each testcase, it is possible to export the coverage data to SQL. This can be stored locally, or fed directly into a database hosted elsewhere.

Coverage merging can also be performed at the end of a regression to combine all test case data.
