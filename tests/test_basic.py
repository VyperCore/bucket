# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2025 Vypercore. All Rights Reserved

import logging
import random
from pathlib import Path
from tempfile import NamedTemporaryFile

from example import example


def test_example():
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger("tb")
    log.setLevel(logging.DEBUG)
    rand = random.Random()

    "Run the example"
    with NamedTemporaryFile("w") as tf:
        example.run_testbench(Path(tf.name), rand, log)
