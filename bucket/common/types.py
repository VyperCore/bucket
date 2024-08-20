# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

from typing import Annotated

from pydantic import AfterValidator


def list_of_lower_str_validator(m_strs: str | list[str]) -> list[str]:
    "Accept a str or list of strings and make them lowercase"
    if isinstance(m_strs, str):
        m_strs = [m_strs]
    m_strs[:] = (m_str.lower() for m_str in m_strs)
    return m_strs


MatchStrs = Annotated[str | list[str], AfterValidator(list_of_lower_str_validator)]
TagStrs = Annotated[str | list[str], AfterValidator(list_of_lower_str_validator)]
