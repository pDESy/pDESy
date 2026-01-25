"""Utility functions for core pDESy logic."""


def build_time_lists_from_state_record(
    state_record_list,
    state_to_bucket: dict,
    finish_margin: float = 1.0,
    buckets: list[str] | None = None,
    include_empty: bool = False,
) -> dict[str, list[tuple[int, int]]]:
    """Build time lists from state records using a state-to-bucket mapping."""
    if buckets is None:
        buckets = sorted({bucket for bucket in state_to_bucket.values() if bucket})
    time_lists = {bucket: [] for bucket in buckets}
    previous_state = None
    from_time = -1
    time = -1
    for time, state in enumerate(state_record_list):
        if state != previous_state:
            if from_time == -1:
                from_time = time
            else:
                bucket = state_to_bucket.get(previous_state)
                if bucket:
                    time_lists[bucket].append(
                        (from_time, (time - 1) - from_time + finish_margin)
                    )
                from_time = time
            previous_state = state

    if from_time > -1:
        bucket = state_to_bucket.get(previous_state)
        if bucket:
            time_lists[bucket].append((from_time, time - from_time + finish_margin))

    if include_empty:
        for bucket in buckets:
            if len(time_lists[bucket]) == 0:
                time_lists[bucket].append((0, 0))

    return time_lists


def print_all_log_in_chronological_order(
    print_log,
    n: int,
    backward: bool = False,
) -> None:
    """Print all logs in chronological order using a print_log callback."""
    if n <= 0:
        return
    step_indices = range(n - 1, -1, -1) if backward else range(n)
    for t in step_indices:
        print("TIME: ", t)
        print_log(t)


def print_basic_log_fields(*fields) -> None:
    """Print log fields in a unified base format."""
    print(*fields)


def build_json_base_dict(instance, **extra) -> dict:
    """Build a base JSON dict with type/name/ID and extra fields."""
    data = {
        "type": instance.__class__.__name__,
        "name": instance.name,
        "ID": instance.ID,
    }
    data.update(extra)
    return data


def read_json_basic_fields(instance, json_data: dict) -> None:
    """Populate common fields from JSON data."""
    instance.name = json_data["name"]
    instance.ID = json_data["ID"]
