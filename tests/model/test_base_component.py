#!/usr/bin/python
# -*- coding: utf-8 -*-

from pDESy.model.base_component import BaseComponent, BaseComponentState
from pDESy.model.base_task import BaseTask, BaseTaskState
from pDESy.model.base_factory import BaseFactory

import datetime


def test_init():
    c1 = BaseComponent("c1")
    assert c1.name == "c1"
    assert len(c1.ID) > 0

    c2 = BaseComponent("c2")
    task = BaseTask("task")
    c = BaseComponent(
        "c",
        ID="xx88xx",
        child_component_list=[c1],
        parent_component_list=[c2],
        targeted_task_list=[task],
        space_size=2.0,
        state=BaseComponentState.FINISHED,
        state_record_list=["aa"],
        placed_factory=BaseFactory("t"),
        placed_factory_id_record=["fff"],
    )
    assert c.name == "c"
    assert c.ID == "xx88xx"
    assert c.child_component_list == [c1]
    assert c.parent_component_list == [c2]
    assert c.targeted_task_list == [task]
    assert c.space_size == 2.0
    assert c.placed_factory.name == "t"
    assert c.placed_factory_id_record == ["fff"]


def test_extend_child_component_list():
    c = BaseComponent("c")
    assert c.parent_component_list == []
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c.extend_child_component_list([c1, c2])
    assert c.child_component_list == [c1, c2]
    assert c1.parent_component_list == [c]
    assert c2.parent_component_list == [c]


def test_append_child_component():
    c = BaseComponent("c")
    assert c.parent_component_list == []
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c.append_child_component(c1)
    c1.append_child_component(c2)
    assert c.child_component_list == [c1]
    assert c1.child_component_list == [c2]
    assert c2.parent_component_list == [c1]
    assert c1.parent_component_list == [c]


def test_set_placed_factory():
    c = BaseComponent("c")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c.append_child_component(c1)
    c1.append_child_component(c2)
    factory = BaseFactory("factory")

    c.set_placed_factory(factory, set_to_all_children=False)
    assert c.placed_factory == factory
    assert c1.placed_factory is None
    assert c2.placed_factory is None

    c.set_placed_factory(factory, set_to_all_children=True)
    assert c.placed_factory == factory
    assert c1.placed_factory == factory
    assert c2.placed_factory == factory


def test_is_ready():
    c = BaseComponent("c")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    c.extend_targeted_task_list([task1, task2])
    assert c.is_ready() is False

    # case 1
    task1.state = BaseTaskState.READY
    assert c.is_ready() is True

    # case 2
    task2.state = BaseTaskState.WORKING
    assert c.is_ready() is False

    # case 3
    task2.state = BaseTaskState.FINISHED
    assert c.is_ready() is True

    # case 4
    task1.state = BaseTaskState.FINISHED
    task2.state = BaseTaskState.FINISHED
    assert c.is_ready() is False


def test_extend_targeted_task_list():
    c = BaseComponent("c")
    assert c.parent_component_list == []
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    c.extend_targeted_task_list([task1, task2])
    assert c.targeted_task_list == [task1, task2]
    assert task1.target_component == c
    assert task2.target_component == c


def test_append_targeted_task():
    c = BaseComponent("c")
    assert c.parent_component_list == []
    task = BaseTask("task1")
    assert task.target_component is None
    c.append_targeted_task(task)
    assert c.targeted_task_list == [task]
    assert task.target_component == c


def test_initialize():
    pass


def test_str():
    print(BaseComponent("c1"))


def test_create_data_for_gantt_plotly():
    c = BaseComponent("c")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    c.extend_targeted_task_list([task1, task2])

    # Set test case (start time = 0, finish time = 5)
    task1.start_time_list = [0, 2]
    task1.ready_time_list = [0, 2]
    task1.finish_time_list = [3, 5]
    task2.start_time_list = [1]
    task2.ready_time_list = [2]
    task2.finish_time_list = [5]
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)

    # timedelta = 1day
    timedelta = datetime.timedelta(days=1)
    df = c.create_data_for_gantt_plotly(init_datetime, timedelta)
    assert df[0]["Start"] == (init_datetime + 0 * timedelta).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    assert df[0]["Finish"] == (init_datetime + (5 + 1.0) * timedelta).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    assert df[0]["Type"] == "Component"


# def test_get_state_record_list():
#     c = BaseComponent("c")
#     task1 = BaseTask("task1")
#     task2 = BaseTask("task2")
#     c.extend_targeted_task_list([task1, task2])

#     # Set test case
#     task1.ready_time_list = [0, 4]
#     task1.start_time_list = [1, 5]
#     task1.finish_time_list = [2, 6]
#     task2.ready_time_list = [1]
#     task2.start_time_list = [2]
#     task2.finish_time_list = [3]

#     assert c.get_state_record_list(auto_task=False) == [
#         BaseTaskState.READY,
#         BaseTaskState.WORKING,
#         BaseTaskState.WORKING,
#         BaseTaskState.FINISHED,
#         BaseTaskState.READY,
#         BaseTaskState.WORKING,
#         BaseTaskState.FINISHED,
#     ]


# def test_get_ready_start_finish_time_list():
#     c = BaseComponent("c")
#     task1 = BaseTask("task1")
#     task2 = BaseTask("task2")
#     c.extend_targeted_task_list([task1, task2])

#     # Set test case
#     task1.ready_time_list = [0, 4]
#     task1.start_time_list = [1, 5]
#     task1.finish_time_list = [2, 6]
#     task2.ready_time_list = [1]
#     task2.start_time_list = [2]
#     task2.finish_time_list = [3]

#     rlist, slist, flist = c.get_ready_start_finish_time_list(auto_task=True)

#     assert rlist == [0, 4]
#     assert slist == [1, 5]
#     assert flist == [3, 6]
