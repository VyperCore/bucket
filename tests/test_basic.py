# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

from tempfile import NamedTemporaryFile

from bucket import example


def test_example():
    "Run the example"
    with NamedTemporaryFile("w") as tf:
        example.run(tf.name)
