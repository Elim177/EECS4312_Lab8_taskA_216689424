from typing import List, Tuple, Optional

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
) -> List[Interval]:
    """
    Returns next N valid appointment slots in chronological order.
    """

    work_start, work_end = working_hours

    # Step 1: normalize busy intervals
    busy = _merge_intervals(busy_intervals)

    # Step 2: apply buffer
    busy = _apply_buffer(busy, buffer)

    # Step 3: merge again after buffer expansion
    busy = _merge_intervals(busy)

    # Step 4: determine search window
    search_start, search_end = work_start, work_end
    if candidate_window:
        clamped = _clamp(candidate_window, working_hours)
        if not clamped:
            return []
        search_start, search_end = clamped

    results = []
    current = search_start

    for start, end in busy:
        if end <= search_start:
            continue
        if start >= search_end:
            break

        gap_start = max(current, search_start)
        gap_end = min(start, search_end)

        if gap_end - gap_start >= duration:
            results.append((gap_start, gap_start + duration))
            if len(results) >= max_results:
                return results

        current = max(current, end)

    # final gap
    if current < search_end:
        if search_end - current >= duration:
            results.append((current, current + duration))

    return results[:max_results]

# REQUIRED NAME (adapter)
def is_allocation_feasible(
    working_hours,
    busy_intervals,
    duration,
    buffer=0,
    candidate_window=None,
    max_results=5,
):
    return recommend_slots(
        working_hours,
        busy_intervals,
        duration,
        buffer,
        candidate_window,
        max_results,
    )