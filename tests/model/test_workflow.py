#!/usr/bin/python
# -*- coding: utf-8 -*-


from pDESy.model.task import Task
import datetime
from pDESy.model.workflow import Workflow
from pDESy.model.base_task import BaseTaskState
from pDESy.model.worker import Worker
from pDESy.model.component import Component
import os


def test_init():
    task1 = Task("task1")
    task1.start_time_list = [1]
    task1.ready_time_list = [0]
    task1.finish_time_list = [3]
    task2 = Task("task2")
    task2.start_time_list = [4]
    task2.ready_time_list = [4]
    task2.finish_time_list = [6]
    task2.append_input_task(task1)
    w = Workflow([task1, task2])
    assert w.task_list == [task1, task2]
    assert w.critical_path_length == 0.0


def test_str():
    print(Workflow([]))


def test_initialize():
    task = Task("task")
    task.est = 2.0
    task.eft = 10.0
    task.lst = 3.0
    task.lft = 11.0
    task.remaining_work_amount = 7
    task.actual_work_amount = 6
    task.state = BaseTaskState.FINISHED
    task.ready_time_list = [1]
    task.start_time_list = [2]
    task.finish_time_list = [15]
    task.additional_task_flag = True
    task.allocated_worker_list = [Worker("w1")]

    task_after1 = Task("task_after1")
    task_after2 = Task("task_after2", default_work_amount=5.0)
    task_after1.append_input_task(task)
    task_after2.append_input_task(task)

    w = Workflow([task, task_after1, task_after2])
    w.critical_path_length = 100.0
    w.initialize()
    assert w.critical_path_length == 20.0
    assert w.task_list[0].est == 0.0
    assert w.task_list[0].eft == 10.0
    assert w.task_list[0].lst == 0.0
    assert w.task_list[0].lft == 10.0
    assert w.task_list[0].state == BaseTaskState.READY
    assert w.task_list[1].est == 10.0
    assert w.task_list[1].eft == 20.0
    assert w.task_list[1].lst == 10.0
    assert w.task_list[1].lft == 20.0
    assert w.task_list[1].state == BaseTaskState.NONE
    assert w.task_list[2].est == 10.0
    assert w.task_list[2].eft == 15.0
    assert w.task_list[2].lst == 15.0
    assert w.task_list[2].lft == 20.0
    assert w.task_list[2].state == BaseTaskState.NONE


def test_update_PERT_data():
    # this method is tested in test_initialize()
    pass


def test_check_state():
    task1 = Task("task1")
    task2 = Task("task2")
    task3 = Task("task3")
    task4 = Task("task4")
    task5 = Task("task5")
    task3.extend_input_task_list([task1, task2])
    task5.extend_input_task_list([task3, task4])
    w = Workflow([task1, task2, task3, task4, task5])

    w1 = Worker("w1", assigned_task_list=[task1])

    # __check_ready test
    task1.state = BaseTaskState.FINISHED
    task2.state = BaseTaskState.FINISHED
    task3.state = BaseTaskState.NONE
    task4.state = BaseTaskState.NONE
    task5.state = BaseTaskState.NONE
    w.check_state(2, BaseTaskState.READY)
    assert task1.state == BaseTaskState.FINISHED
    assert task2.state == BaseTaskState.FINISHED
    assert task3.state == BaseTaskState.READY
    assert task4.state == BaseTaskState.READY
    assert task5.state == BaseTaskState.NONE

    # __check_working test
    task1.state = BaseTaskState.READY
    task2.state = BaseTaskState.READY
    task2.allocated_worker_list = [w1]
    task3.state = BaseTaskState.NONE
    task4.state = BaseTaskState.NONE
    task5.state = BaseTaskState.NONE
    w.check_state(2, BaseTaskState.WORKING)
    assert task1.state == BaseTaskState.READY
    assert task2.state == BaseTaskState.WORKING
    assert task3.state == BaseTaskState.NONE
    assert task4.state == BaseTaskState.NONE
    assert task5.state == BaseTaskState.NONE

    # __check_finished test

    task1.state = BaseTaskState.WORKING
    task1.allocated_worker_list = [w1]
    task1.remaining_work_amount = 0.0
    task2.state = BaseTaskState.FINISHED
    task3.state = BaseTaskState.NONE
    task4.state = BaseTaskState.NONE
    task5.state = BaseTaskState.NONE
    w.check_state(2, BaseTaskState.FINISHED)
    assert task1.state == BaseTaskState.FINISHED
    assert task2.state == BaseTaskState.FINISHED
    assert task3.state == BaseTaskState.NONE
    assert task4.state == BaseTaskState.NONE
    assert task5.state == BaseTaskState.NONE


def test___check_ready():
    # this method is tested in test_check_state()
    pass


def test___check_working():
    # this method is tested in test_check_state()
    pass


def test___check_finished():
    # this method is tested in test_check_state()
    pass


def test___set_est_eft_data():
    # this method is tested in test_initialize()
    pass


def test___set_lst_lft_criticalpath_data():
    # this method is tested in test_initialize()
    pass


def test_perform():
    task = Task("task")
    task.state = BaseTaskState.WORKING
    w1 = Worker("w1")
    w2 = Worker("w2")
    w1.workamount_skill_mean_map = {"task": 1.0}
    task.allocated_worker_list = [w1, w2]
    w1.assigned_task_list = [task]
    w2.assigned_task_list = [task]
    c = Component("a")
    c.append_targeted_task(task)
    w = Workflow([task])
    w.perform(10)
    assert task.remaining_work_amount == task.default_work_amount - 1.0
    assert task.target_component == c
    assert c.error == 0.0


def test_create_simple_gantt():
    task0 = Task("auto", auto_task=True)
    task0.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task1 = Task("task1")
    task1.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2 = Task("task2")
    task2.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2.append_input_task(task1)
    w = Workflow([task1, task2, task0])
    w.create_simple_gantt(finish_margin=1.0, view_auto_task=True, view_ready=False)
    w.create_simple_gantt(
        view_ready=True, view_auto_task=True, save_fig_path="test.png"
    )
    if os.path.exists("test.png"):
        os.remove("test.png")


def test_create_data_for_gantt_plotly():
    task1 = Task("task1")
    task1.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2 = Task("task2")
    task2.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2.append_input_task(task1)
    w = Workflow([task1, task2])
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    w.create_data_for_gantt_plotly(init_datetime, timedelta, view_ready=True)


def test_create_gantt_plotly():
    task1 = Task("task1")
    task1.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2 = Task("task2")
    task2.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2.append_input_task(task1)
    w = Workflow([task1, task2])
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    w.create_gantt_plotly(init_datetime, timedelta, save_fig_path="test.png")
    if os.path.exists("test.png"):
        os.remove("test.png")


def test_get_networkx_graph():
    task1 = Task("task1")
    task1.start_time_list = [1]
    task1.ready_time_list = [0]
    task1.finish_time_list = [3]
    task2 = Task("task2")
    task2.start_time_list = [4]
    task2.ready_time_list = [4]
    task2.finish_time_list = [6]
    task2.append_input_task(task1)
    w = Workflow([task1, task2])
    w.get_networkx_graph()
    # TODO
    # assert...


def test_draw_networkx():
    task0 = Task("auto", auto_task=True)
    task1 = Task("task1")
    task1.start_time_list = [1]
    task1.ready_time_list = [0]
    task1.finish_time_list = [3]
    task2 = Task("task2")
    task2.start_time_list = [4]
    task2.ready_time_list = [4]
    task2.finish_time_list = [6]
    task2.append_input_task(task1)
    w = Workflow([task1, task2, task0])
    w.draw_networkx(save_fig_path="test.png")
    if os.path.exists("test.png"):
        os.remove("test.png")


def test_get_node_and_edge_trace_for_plotly_network():
    task1 = Task("task1")
    task1.start_time_list = [1]
    task1.ready_time_list = [0]
    task1.finish_time_list = [3]
    task2 = Task("task2")
    task2.start_time_list = [4]
    task2.ready_time_list = [4]
    task2.finish_time_list = [6]
    task2.append_input_task(task1)
    w = Workflow([task1, task2])
    (
        task_node_trace,
        auto_task_node_trace,
        edge_trace,
    ) = w.get_node_and_edge_trace_for_plotly_network()
    # TODO
    # assert...
    (
        task_node_trace,
        auto_task_node_trace,
        edge_trace,
    ) = w.get_node_and_edge_trace_for_plotly_network()
    # TODO
    # assert...


def test_draw_plotly_network():
    task0 = Task("auto", auto_task=True)
    task1 = Task("task1")
    task1.start_time_list = [1]
    task1.ready_time_list = [0]
    task1.finish_time_list = [3]
    task2 = Task("task2")
    task2.start_time_list = [4]
    task2.ready_time_list = [4]
    task2.finish_time_list = [6]
    task2.append_input_task(task1)
    w = Workflow([task1, task2, task0])
    w.draw_plotly_network(save_fig_path="test.png")
    if os.path.exists("test.png"):
        os.remove("test.png")
