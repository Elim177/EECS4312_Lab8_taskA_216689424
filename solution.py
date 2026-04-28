from typing import List, Tuple, Optional, Dict, Any

Time = int  # minutes since midnight
Interval = Tuple[Time, Time]


def _merge_intervals(intervals: List[Interval]) -> List[Interval]:
    if not intervals:
        return []

    intervals = sorted(intervals)
    merged = [intervals[0]]

    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]

        if start <= last_end:  # overlap or adjacent
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))

    return merged


def _apply_buffer(intervals: List[Interval], buffer: int) -> List[Interval]:
    return [(start - buffer, end + buffer) for start, end in intervals]


def _clamp(interval: Interval, bounds: Interval) -> Optional[Interval]:
    start = max(interval[0], bounds[0])
    end = min(interval[1], bounds[1])
    return (start, end) if start < end else None


def recommend_slots(
    working_hours: Interval,
    busy_intervals: List[Interval],
    duration: int,
    buffer: int = 0,
    candidate_window: Optional[Interval] = None,
    max_results: int = 5,
    include_explanations: bool = False,  # NEW
) -> Dict[str, Any]:
    """
    Returns:
    {
        "slots": List[Interval],
        "meta": {
            "reason": str (only if needed),
            "steps": List[str] (optional, if explanations enabled)
        }
    }
    """

    meta: Dict[str, Any] = {}
    steps: List[str] = []

    work_start, work_end = working_hours

    # Step 1: normalize busy intervals
    busy = _merge_intervals(busy_intervals)
    if include_explanations:
        steps.append(f"Merged busy intervals → {busy}")

    # Step 2: apply buffer
    busy = _apply_buffer(busy, buffer)
    if include_explanations:
        steps.append(f"Applied buffer ({buffer} mins) → {busy}")

    # Step 3: merge again
    busy = _merge_intervals(busy)
    if include_explanations:
        steps.append(f"Re-merged intervals → {busy}")

    # Step 4: determine search window
    search_start, search_end = work_start, work_end

    if candidate_window:
        clamped = _clamp(candidate_window, working_hours)

        if not clamped:
            meta["reason"] = "Candidate window outside working hours."
            if include_explanations:
                meta["steps"] = steps
            return {"slots": [], "meta": meta}

        search_start, search_end = clamped
        if include_explanations:
            steps.append(f"Clamped search window → {clamped}")

    results: List[Interval] = []
    current = search_start

    for start, end in busy:
        if end <= search_start:
            continue
        if start >= search_end:
            break

        gap_start = max(current, search_start)
        gap_end = min(start, search_end)

        if gap_end - gap_start >= duration:
            slot = (gap_start, gap_start + duration)
            results.append(slot)

            if include_explanations:
                steps.append(f"Selected slot {slot} from gap ({gap_start}, {gap_end})")

            if len(results) >= max_results:
                break

        current = max(current, end)

    # final gap
    if len(results) < max_results and current < search_end:
        if search_end - current >= duration:
            slot = (current, current + duration)
            results.append(slot)

            if include_explanations:
                steps.append(f"Selected final slot {slot}")

    # Handle empty results explicitly (NO silent failure)
    if not results:
        meta["reason"] = "No available slots meet duration and buffer constraints."

    if include_explanations:
        meta["steps"] = steps

    return {"slots": results[:max_results], "meta": meta}


# REQUIRED NAME (adapter)
def is_allocation_feasible(
    working_hours,
    busy_intervals,
    duration,
    buffer=0,
    candidate_window=None,
    max_results=5,
    include_explanations=False,
):
    return recommend_slots(
        working_hours,
        busy_intervals,
        duration,
        buffer,
        candidate_window,
        max_results,
        include_explanations,
    )