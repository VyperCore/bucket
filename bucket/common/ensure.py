# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2025 Vypercore. All Rights Reserved


def ensure(condition, error_type, message):
    """
    Ensure that a condition is true. If not, raise an exception.
    Using a central function for this allows for easier debugging and testing.
    :param condition: The condition to check
    :param error_type: The type of exception to raise
    :param message: The message to include in the exception
    """
    if not condition:
        raise error_type(message)


def raise_assertion(error_type, message):
    """
    For when you want to raise an exception without a condition.
    :param error_type: The type of exception to raise
    :param message: The message to include in the exception
    """
    ensure(False, error_type, message)
