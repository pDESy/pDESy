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


class SingleNodeLogJsonMixin:
    """Mixin for log printing and JSON export/import (single node)."""

    def _get_log_extra_fields(self, target_step_time: int) -> list:
        return []

    def _get_export_dict_extra_fields(self) -> dict:
        return {}

    def _read_json_extra_fields(self, json_data: dict) -> None:
        for spec in self._get_read_json_field_specs():
            if len(spec) == 1:
                attr_name = spec[0]
                json_key = attr_name
                converter = None
            elif len(spec) == 2:
                attr_name, second = spec
                if callable(second):
                    json_key = attr_name
                    converter = second
                else:
                    json_key = second
                    converter = None
            else:
                attr_name, json_key, converter = spec
            value = json_data[json_key]
            if converter is not None:
                value = converter(value)
            setattr(self, attr_name, value)

    def _get_read_json_field_specs(self):
        return []

    def print_log(self, target_step_time: int) -> None:
        """Print log in `target_step_time`."""
        print_basic_log_fields(
            self.ID,
            self.name,
            self.state_record_list[target_step_time],
            *self._get_log_extra_fields(target_step_time),
        )

    def print_all_log_in_chronological_order(self, backward: bool = False) -> None:
        """Print all log in chronological order."""
        print_all_log_in_chronological_order(
            self.print_log, len(self.state_record_list), backward
        )

    def export_dict_json_data(self):
        """Export the information to JSON data."""
        return build_json_base_dict(self, **self._get_export_dict_extra_fields())

    def read_json_data(self, json_data: dict) -> None:
        """Read the JSON data for this instance."""
        read_json_basic_fields(self, json_data)
        self._read_json_extra_fields(json_data)


class CollectionLogJsonMixin:
    """Mixin for collection log printing and JSON export/import."""

    def _iter_log_children(self):
        return ()

    def _get_log_length(self) -> int:
        children = list(self._iter_log_children())
        if not children:
            return 0
        return len(children[0].state_record_list)

    def _get_export_dict_extra_fields(self) -> dict:
        return {}

    def _read_json_extra_fields(self, json_data: dict) -> None:
        return None

    def print_log(self, target_step_time: int):
        """Print log in `target_step_time`."""
        for child in self._iter_log_children():
            child.print_log(target_step_time)

    def print_all_log_in_chronological_order(self, backward: bool = False):
        """Print all log in chronological order."""
        n = self._get_log_length()
        if n > 0:
            print_all_log_in_chronological_order(self.print_log, n, backward)

    def export_dict_json_data(self):
        """Export the information to JSON data."""
        return build_json_base_dict(self, **self._get_export_dict_extra_fields())

    def read_json_data(self, json_data: dict) -> None:
        """Read the JSON data for this instance."""
        read_json_basic_fields(self, json_data)
        self._read_json_extra_fields(json_data)


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


class AssignedPairsMixin:
    """Mixin for managing assigned pairs as an immutable set."""

    _assigned_pairs_attr_name: str = ""

    def _get_assigned_pairs(self):
        return getattr(self, self._assigned_pairs_attr_name)

    def _set_assigned_pairs(self, pairs):
        setattr(self, self._assigned_pairs_attr_name, pairs)

    def set_assigned_pairs(self, pairs_iterable):
        """Set assigned pairs (non-destructive)."""
        self._set_assigned_pairs(frozenset(pairs_iterable))

    def add_assigned_pair(self, pair: tuple[str, str]):
        """Add one assigned pair (non-destructive)."""
        cur = self._get_assigned_pairs()
        if pair in cur:
            return
        self._set_assigned_pairs(frozenset((*cur, pair)))

    def remove_assigned_pair(self, pair: tuple[str, str]):
        """Remove one assigned pair (non-destructive)."""
        cur = self._get_assigned_pairs()
        if pair not in cur:
            return
        self._set_assigned_pairs(frozenset(x for x in cur if x != pair))

    def update_assigned_pairs(self, add=(), remove=()):
        """Update assigned pairs (non-destructive)."""
        cur = self._get_assigned_pairs()
        if not add and not remove:
            return
        s = set(cur)
        if remove:
            s.difference_update(remove)
        if add:
            s.update(add)
        self._set_assigned_pairs(frozenset(s))


class WorkerFacilityCommonMixin:
    """Mixin for shared worker/facility behavior."""

    _state_record_attr_name: str = "state_record_list"
    _cost_record_attr_name: str = "cost_record_list"
    _assigned_record_attr_name: str = ""
    _assigned_pairs_attr_name: str = ""
    _state_free_value = None
    _state_working_value = None
    _state_absence_value = None

    def _get_record(self, attr_name: str):
        return getattr(self, attr_name)

    def _set_record(self, attr_name: str, value):
        setattr(self, attr_name, value)

    def initialize(self, state_info: bool = True, log_info: bool = True):
        """
        Initialize the changeable variables.

        Args:
            state_info (bool, optional): Whether to initialize state information.
            log_info (bool, optional): Whether to initialize log information.
        """
        if state_info:
            self.state = self._state_free_value
            setattr(self, self._assigned_pairs_attr_name, frozenset())

        if log_info:
            self._set_record(self._state_record_attr_name, [])
            self._set_record(self._cost_record_attr_name, [])
            self._set_record(self._assigned_record_attr_name, [])

    def reverse_log_information(self):
        """Reverse log information of all records."""
        self._get_record(self._state_record_attr_name).reverse()
        self._get_record(self._cost_record_attr_name).reverse()
        self._get_record(self._assigned_record_attr_name).reverse()

    def record_assigned_task_id(self):
        """Record assigned task id to assigned record list."""
        assigned_pairs = getattr(self, self._assigned_pairs_attr_name)
        self._get_record(self._assigned_record_attr_name).append(assigned_pairs)

    def record_state(self, working: bool = True):
        """Record current state in state record list."""
        record = self._get_record(self._state_record_attr_name)
        if working:
            record.append(self.state)
        else:
            record.append(self._state_absence_value)

    def remove_absence_time_list(self, absence_time_list: list[int]):
        """Remove record information on `absence_time_list`."""
        state_record = self._get_record(self._state_record_attr_name)
        assigned_record = self._get_record(self._assigned_record_attr_name)
        cost_record = self._get_record(self._cost_record_attr_name)
        for step_time in sorted(absence_time_list, reverse=True):
            if step_time < len(state_record):
                assigned_record.pop(step_time)
                cost_record.pop(step_time)
                state_record.pop(step_time)

    def insert_absence_time_list(self, absence_time_list: list[int]):
        """Insert record information on `absence_time_list`."""
        state_record = self._get_record(self._state_record_attr_name)
        assigned_record = self._get_record(self._assigned_record_attr_name)
        cost_record = self._get_record(self._cost_record_attr_name)
        for step_time in sorted(absence_time_list):
            if step_time < len(state_record):
                if step_time == 0:
                    assigned_record.insert(step_time, None)
                    cost_record.insert(step_time, 0.0)
                    state_record.insert(step_time, self._state_free_value)
                else:
                    assigned_record.insert(step_time, assigned_record[step_time - 1])
                    cost_record.insert(step_time, 0.0)
                    state_record.insert(step_time, self._state_free_value)

    def check_update_state_from_absence_time_list(self, step_time: int):
        """
        Check and update state to absence, free, or working.
        """
        if step_time in self.absence_time_list:
            self.state = self._state_absence_value
            return
        assigned = getattr(self, self._assigned_pairs_attr_name)
        self.state = self._state_free_value if not assigned else self._state_working_value

    def get_time_list_for_gantt_chart(self, finish_margin: float = 1.0):
        """
        Get ready/working/absence time_list for drawing Gantt chart.
        """
        state_record = self._get_record(self._state_record_attr_name)
        state_to_bucket = {
            self._state_free_value: "ready",
            self._state_working_value: "working",
            self._state_absence_value: "absence",
        }
        time_lists = build_time_lists_from_state_record(
            state_record,
            state_to_bucket=state_to_bucket,
            finish_margin=finish_margin,
            buckets=["ready", "working", "absence"],
            include_empty=True,
        )
        return time_lists["ready"], time_lists["working"], time_lists["absence"]

    def __str__(self):
        """Return the name of the instance."""
        return f"{self.name}"

    def has_workamount_skill(self, task_name: str, error_tol: float = 1e-10):
        """
        Check whether this instance has workamount skill for a given task.
        """
        if task_name in self.workamount_skill_mean_map:
            if self.workamount_skill_mean_map[task_name] > 0.0 + error_tol:
                return True
        return False


class ComponentTaskCommonMixin:
    """Mixin for component/task shared behavior."""

    _absence_state_record_attr_name: str = ""
    _absence_aux_record_attr_names: list[str] = []
    _absence_initial_state_value = None
    _absence_state_working_value = None
    _absence_state_ready_value = None
    _absence_state_finished_value = None
    _absence_state_none_value = None

    def _get_absence_record(self, attr_name: str):
        return getattr(self, attr_name)

    def _get_absence_aux_initial_value(self, attr_name: str):
        return None

    def _get_absence_aux_insert_value(self, record, attr_name: str, step_time: int):
        if step_time == 0:
            return self._get_absence_aux_initial_value(attr_name)
        return record[step_time - 1]

    def _resolve_absence_insert_state(self, before_state, after_state):
        if before_state == self._absence_state_working_value:
            if after_state == self._absence_state_finished_value:
                return self._absence_state_finished_value
            return self._absence_state_ready_value
        if (
            before_state == self._absence_state_none_value
            and after_state == self._absence_state_working_value
        ):
            return self._absence_state_ready_value
        return before_state

    def remove_absence_time_list(self, absence_time_list: list[int]) -> None:
        """Remove record information on `absence_time_list`."""
        state_record = self._get_absence_record(self._absence_state_record_attr_name)
        aux_records = [
            self._get_absence_record(attr_name)
            for attr_name in self._absence_aux_record_attr_names
        ]
        for step_time in sorted(absence_time_list, reverse=True):
            if step_time < len(state_record):
                for record in aux_records:
                    record.pop(step_time)
                state_record.pop(step_time)

    def insert_absence_time_list(self, absence_time_list: list[int]) -> None:
        """Insert record information on `absence_time_list`."""
        state_record = self._get_absence_record(self._absence_state_record_attr_name)
        aux_records = [
            (attr_name, self._get_absence_record(attr_name))
            for attr_name in self._absence_aux_record_attr_names
        ]
        for step_time in sorted(absence_time_list):
            if step_time < len(state_record):
                for attr_name, record in aux_records:
                    record.insert(
                        step_time,
                        self._get_absence_aux_insert_value(
                            record, attr_name, step_time
                        ),
                    )
                if step_time == 0:
                    state_record.insert(step_time, self._absence_initial_state_value)
                else:
                    insert_state_before = state_record[step_time - 1]
                    insert_state_after = state_record[step_time]
                    state_record.insert(
                        step_time,
                        self._resolve_absence_insert_state(
                            insert_state_before, insert_state_after
                        ),
                    )


class CollectionCommonMixin:
    """Mixin for collection shared behavior."""

    _absence_cost_record_attr_name: str | None = None

    def _iter_absence_children(self):
        return ()

    def _iter_log_children(self):
        return ()

    def _get_reverse_log_lists(self) -> list[list]:
        return []

    def _record_child_before_state(self, child) -> None:
        return None

    def remove_absence_time_list(self, absence_time_list: list[int]) -> None:
        """Remove record information on `absence_time_list`."""
        for child in self._iter_absence_children():
            child.remove_absence_time_list(absence_time_list)
        if self._absence_cost_record_attr_name:
            cost_record = getattr(self, self._absence_cost_record_attr_name)
            for step_time in sorted(absence_time_list, reverse=True):
                if step_time < len(cost_record):
                    cost_record.pop(step_time)

    def insert_absence_time_list(self, absence_time_list: list[int]) -> None:
        """Insert record information on `absence_time_list`."""
        for child in self._iter_absence_children():
            child.insert_absence_time_list(absence_time_list)
        if self._absence_cost_record_attr_name:
            cost_record = getattr(self, self._absence_cost_record_attr_name)
            for step_time in sorted(absence_time_list):
                cost_record.insert(step_time, 0.0)

    def reverse_log_information(self):
        """Reverse log information of all."""
        for record_list in self._get_reverse_log_lists():
            record_list.reverse()
        for child in self._iter_log_children():
            child.reverse_log_information()

    def record_children_assigned_task_id(self):
        """Record assigned task ids for all children."""
        for child in self._iter_log_children():
            child.record_assigned_task_id()

    def record_children_state(self, working: bool = True):
        """Record state for all children."""
        for child in self._iter_log_children():
            child.record_state(working=working)

    def record(self, working: bool = True):
        """Record child log information."""
        for child in self._iter_log_children():
            self._record_child_before_state(child)
            child.record_state(working=working)
