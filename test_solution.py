from solution import recommend_slots
from solution import is_allocation_feasible

import pytest
from solution import is_allocation_feasible


# ----------------------------
# C1: Time Gap Validity Constraint
# ----------------------------
# Validates AC1, AC6
def test_working_hours_boundary():
    working_hours = (540, 1020)
    busy = [(600, 660)]

    result = is_allocation_feasible(
        working_hours,
        busy,
        duration=30
    )

    for slot in result:
        assert working_hours[0] <= slot[0] and slot[1] <= working_hours[1]


# ----------------------------
# C2: Buffer Enforcement Constraint
# ----------------------------
# Validates AC3
def test_buffer_compliance():
    working_hours = (540, 1020)
    busy = [(600, 660)]

    result = is_allocation_feasible(
        working_hours,
        busy,
        duration=30,
        buffer=30
    )

    # buffered busy becomes (570, 690)
    for slot in result:
        assert not (570 <= slot[0] < 690)


# ----------------------------
# C3: Interval Normalization Constraint
# ----------------------------
# Validates AC2, AC6
def test_overlapping_busy_intervals():
    working_hours = (540, 1020)
    busy = [(630, 700), (600, 650)]

    result = is_allocation_feasible(
        working_hours,
        busy,
        duration=30
    )

    # merged busy becomes (600, 700)
    for slot in result:
        # slot must NOT start inside busy interval
        assert not (600 <= slot[0] < 700)


# ----------------------------
# C4: Minimum Duration Constraint
# ----------------------------
# Validates AC4
def test_minimum_duration():
    working_hours = (540, 600)
    busy = []

    result = is_allocation_feasible(
        working_hours,
        busy,
        duration=90
    )

    assert result == []  # no valid slot possible


# ----------------------------
# C5: Availability Constraint
# ----------------------------
# Validates edge case of no availability
def test_no_availability():
    working_hours = (540, 600)
    busy = [(540, 600)]

    result = is_allocation_feasible(
        working_hours,
        busy,
        duration=15
    )

    assert result == []


# ----------------------------
# C6: Output Ordering Constraint
# ----------------------------
# Validates AC5
def test_chronological_ordering():
    working_hours = (540, 1020)
    busy = [(600, 660), (720, 780)]

    result = is_allocation_feasible(
        working_hours,
        busy,
        duration=30
    )

    starts = [slot[0] for slot in result]
    assert starts == sorted(starts)

# for the allocation
def test_is_allocation_feasible_no_availability():
    working_hours = (540, 600)  # 9:00–10:00
    busy_intervals = [(540, 600)]  # fully booked

    result = is_allocation_feasible(
        working_hours,
        busy_intervals,
        duration=30
    )

    assert result == []