# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved


class AxisUtils:
    """Common utils for Axes"""

    def one_hot(
        width: int = None,
        display_bin: bool = False,
        display_hex: bool = False,
        pad_zero: bool = True,
    ):
        """
        Creates an axis with one-hot encoding up to the requested width (in bits). Includes zero.
        Bucket name will display in binary/hexadecimal automatically based on width.

        Parameters:
            width: Number of bits
            display_bin: Override bucket name to display as binary (Default: False)
            display_hex: Override bucket name to display as hexadecimal (Default: False)
            pad_zero: Pad bucket name with leading zeroes. (Default: True)

            Returns: Dict of {bucket_name: value}

        """
        assert width > 0, f"Width must be 1+ for one_hot_axis. Recieved: {width}"
        assert not (
            display_bin and display_hex
        ), "Either display_bin OR display_hex may be set for one_hot"

        if not (display_bin or display_hex):
            if width < 8:
                display_bin = True
            else:
                display_hex = True

        one_hot_vals = [0]
        for i in range(width):
            one_hot_vals.append(1 << i)

        if display_bin:
            pad = width if pad_zero else 0
            one_hot_dict = {f"0b{v:0{pad}b}": v for v in one_hot_vals}
        elif display_hex:
            # Count hexadecimal bits plus underscores
            pad = (((width - 1) // 4) + 1 + ((width - 1) // 16)) if pad_zero else 0
            one_hot_dict = {f"0x{v:0{pad}_x}": v for v in one_hot_vals}

        return one_hot_dict

    def msb(
        width: int = None,
        display_bin: bool = False,
        display_hex: bool = False,
        pad_zero: bool = True,
        include_max=False,
    ):
        """
        Creates an axis with one-hot encoding up to the requested width (in bits), with the
        full range of values. Includes zero. Bucket name will display in binary/hexadecimal
        automatically based on width.

        Parameters:
            width: Number of bits
            display_bin: Override bucket name to display as binary (Default: False)
            display_hex: Override bucket name to display as hexadecimal (Default: False)
            pad_zero: Pad bucket name with leading zeroes. (Default: True)
            include_maxX: Include all-ones (Default: False)

            Returns: Dict of {bucket_name: value_range}

        """
        assert width > 1, f"Width must be 2+ for msb_axis. Recieved: {width}"
        assert not (
            display_bin and display_hex
        ), "Either display_bin OR display_hex may be set for msb"

        if not (display_bin or display_hex):
            if width < 8:
                display_bin = True
            else:
                display_hex = True

        if include_max:
            max_val = (1 << width) - 1

        msb_vals = [0]
        for i in range(width):
            msb_vals.append(1 << i)
        if include_max:
            msb_vals.append(max_val)

        def val_range(msb_val):
            if msb_val == 0:
                u = 0
                l = 0
            elif include_max and (msb_val == max_val):
                u = max_val
                l = max_val
            else:
                if include_max and (msb_val == 1 << (width - 1)):
                    u = (msb_val << 1) - 2
                else:
                    u = (msb_val << 1) - 1
                l = msb_val
            return [l, u]

        if display_bin:
            pad = width if pad_zero else 0
            msb_dict = {f"0b{v:0{pad}b}": val_range(v) for v in msb_vals}
        elif display_hex:
            # Count hexadecimal bits plus underscores
            pad = (((width - 1) // 4) + 1 + ((width - 1) // 16)) if pad_zero else 0
            msb_dict = {f"0x{v:0{pad}_x}": val_range(v) for v in msb_vals}

        return msb_dict
