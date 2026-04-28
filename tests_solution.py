import pytest

from solution import recommend_slots


# ---------- BASIC FUNCTIONALITY ----------

def test_simple_gap():
    result = recommend_slots(
        working_hours=(540, 1020),
        busy_intervals=[(600, 660)],
        duration=30,
    )

    assert result["slots"][0] == (540, 570)


def test_multiple_slots_ordered():
    result = recommend_slots(
        working_hours=(540, 1020),
        busy_intervals=[(600, 660), (700, 760)],
        duration=30,
        max_results=3,
    )

    slots = result["slots"]
    assert slots == sorted(slots)  # deterministic ordering
    assert len(slots) <= 3


# ---------- BUFFER HANDLING ----------

def test_buffer_blocks_slot():
    result = recommend_slots(
        working_hours=(540, 700),
        busy_intervals=[(600, 620)],
        duration=30,
        buffer=20,
    )

    # buffer expands to (580, 640), blocking expected slot
    assert all(not (580 <= s[0] < 640) for s in result["slots"])


# ---------- CANDIDATE WINDOW ----------

def test_candidate_window_clamping():
    result = recommend_slots(
        working_hours=(540, 1020),
        busy_intervals=[],
        duration=60,
        candidate_window=(0, 600),
    )

    # clamped to working hours → (540, 600)
    assert result["slots"][0] == (540, 600)


def test_candidate_window_outside():
    result = recommend_slots(
        working_hours=(540, 1020),
        busy_intervals=[],
        duration=60,
        candidate_window=(0, 500),
    )

    assert result["slots"] == []
    assert "reason" in result["meta"]


# ---------- NO SILENT FAILURE ----------

def test_no_available_slots_returns_reason():
    result = recommend_slots(
        working_hours=(540, 600),
        busy_intervals=[(540, 600)],
        duration=30,
    )

    assert result["slots"] == []
    assert result["meta"]["reason"] is not None


# ---------- EXPLANATION MODE ----------

def test_explanations_present_when_enabled():
    result = recommend_slots(
        working_hours=(540, 1020),
        busy_intervals=[(600, 660)],
        duration=30,
        include_explanations=True,
    )

    assert "steps" in result["meta"]
    assert len(result["meta"]["steps"]) > 0


def test_explanations_absent_when_disabled():
    result = recommend_slots(
        working_hours=(540, 1020),
        busy_intervals=[(600, 660)],
        duration=30,
        include_explanations=False,
    )

    assert "steps" not in result["meta"]


# ---------- EDGE CASES ----------

def test_adjacent_intervals_merge():
    result = recommend_slots(
        working_hours=(540, 800),
        busy_intervals=[(600, 650), (650, 700)],  # adjacent
        duration=30,
    )

    # should behave as one block (600–700)
    for slot in result["slots"]:
        assert not (600 <= slot[0] < 700)


def test_zero_busy_intervals():
    result = recommend_slots(
        working_hours=(540, 600),
        busy_intervals=[],
        duration=30,
    )

    assert result["slots"][0] == (540, 570)


def test_exact_fit_gap():
    result = recommend_slots(
        working_hours=(540, 600),
        busy_intervals=[(570, 600)],
        duration=30,
    )

    assert result["slots"][0] == (540, 570)



# ---------- DETERMINISM ----------

def test_deterministic_output():
    inputs = dict(
        working_hours=(540, 1020),
        busy_intervals=[(700, 760), (600, 660)],  # unsorted input
        duration=30,
    )

    result1 = recommend_slots(**inputs)
    result2 = recommend_slots(**inputs)

    assert result1 == result2