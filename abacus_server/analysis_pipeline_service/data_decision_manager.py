
from dataclasses import dataclass
import dataclasses
import os
from os import name, path
import importlib.util
from importlib.machinery import SourceFileLoader
import threading
from dataclasses import dataclass, field
from ..global_events import global_events_manager
import queue
import typing
from ..models.analysis_pipeline_models import DataDecisionInput
from pydantic import validate_arguments

class DecisionQueue:
    def __init__(self, input_signal="data_analysis_manager"):
        """Needs to store the last message recieved for a given data request function. 
            When these are not None the DataDecision will make its first decision"""
        self.input_signal = input_signal
        global_events_manager.connect(self.reciever, self.input_signal)

        self.parent_dir: str = path.dirname(__file__)
        self.data_decisions_filepath: str = self.parent_dir + "\data_decisions"
        self.data_decisions = self.fetch_data_decisions()

    def reciever(self, sender, message):
        """message is a dict with 
            Keys:
                name_tag: name of the DataSource object that data is originating from
                source_results: results from the service function that the DataSource object requested data from 
                function_params: parameters/arguements given to the service function. Should be the same as the target_function dict
                analysis_results: results from the analysis with the name <name_tag>
                """

        print(f"DataDecision Recieved a message from {sender}")
        print(f"DECISION MESSAGE {message.keys()}")
        try:

            pipeline_name = message['name_tag']
            data_source_t_func = list(message['source_results'].keys())[0]

            data_decision_object = self.data_decisions[pipeline_name]
            data_decision_object.required_inputs = message

            # print(
            #     f"Target {data_source_t_func} Decisions input data: {self.data_decisions[pipeline_name].required_inputs}")
            #print(f"ENOUGH DATA? {data_decision_object.has_enough_data()}")

            if data_decision_object.has_enough_data():
                print(f"READY TO MAKE A DECISION ON {pipeline_name}")
                try:
                    data_decision_object.run()
                except Exception as e:
                    print(
                        f"ERROR {e} occured in the run function for {pipeline_name}")

            else:
                print(
                    f"DataDecision for {pipeline_name} does not have enough data to make a decision")

        except Exception as e:
            print(f"DataDecision could not interpret message from {sender}")

    def fetch_data_decisions(self):
        decisions = {}
        try:

            for file in os.listdir(self.data_decisions_filepath):
                if file.endswith("_decision.py"):
                    file_endpoint = f"\{file}"
                    file_path = self.data_decisions_filepath + file_endpoint
                    pipe_module = SourceFileLoader(
                        file_endpoint, file_path).load_module()

                    data_decisions = pipe_module.DataDecision()
                    decisions.update({data_decisions.name_tag: data_decisions})
                    print(f"Fetching decisions: {decisions}")
        except Exception as e:
            print(
                f"ERROR: {e} data_analysis_manager could not parse data_analyses directory")
        return decisions


class DataDecisionManager:
    def __init__(self, input_signal="data_analysis_manager") -> None:
        """Needs to store the last message recieved for a given data request function. 
            When these are not None the DataDecision will make its first decision"""
        self.input_signal = input_signal
        global_events_manager.connect(self.reciever, self.input_signal)

        self.data_decisions = {}
        self._events_queue = self._EventQueue()
        self.runner = self._Runner(events_queue=self._events_queue)
        self.runner.start()

    def terminate(self):
        self.runner.stop()

    def add_decision(self, decision_obj):
        self.data_decisions.update({decision_obj.name_tag: decision_obj})

    def add_many_decisions(self, decison_obj_list):
        for decision_obj in decison_obj_list:
            self.add_decision(decision_obj)

    @validate_arguments
    def reciever(self, sender, signal, message: DataDecisionInput):
        """message is a dict with 
            Keys:
                name_tag: name of the DataSource object that data is originating from
                source_results: results from the service function that the DataSource object requested data from 
                function_params: parameters/arguements given to the service function. Should be the same as the target_function dict
                analysis_results: results from the analysis with the name <name_tag>
                """
        print(f"DataDecision Recieved a message from {sender}")

        try:
            message = message.dict()
            pipeline_name = message['name_tag']
            data_source_t_func = list(message['source_results'].keys())[0]

            data_decision_object = self.data_decisions[pipeline_name]
            data_decision_object.update_input(data_source_t_func, message)

            # print(
            #     f"Target {data_source_t_func} Decisions input data: {self.data_decisions[pipeline_name].required_inputs}")
            #print(f"ENOUGH DATA? {data_decision_object.has_enough_data()}")

            if data_decision_object.has_enough_data():

                """Enqueue the decision to be made"""
                self._events_queue.enqueue(
                    event=data_decision_object, priority=3)

                # print(f"READY TO MAKE A DECISION ON {pipeline_name}")
                # try:
                #     data_decision_object.run()
                # except Exception as e:
                #     print(
                #         f"ERROR {e} occured in the run function for {pipeline_name}")

            else:
                print(
                    f"DataDecision for {pipeline_name} does not have enough data to make a decision")

        except Exception as e:
            print(f"DataDecision could not interpret message from {sender}")

    class _EventQueue:
        def __init__(self) -> None:
            """A queue where events are placed and wait to be called. Queue is a priority queue with a default priority of 3.
            Intent is to be able to set high priority items(priority=1) and medium priority items(priority=2)"""
            self._queue = queue.PriorityQueue(maxsize=100)
            self._condition = threading.Condition()

        def __len__(self):
            return self._queue.qsize()

        def enqueue(self, event, priority: int = 3):
            with self._condition:
                self._queue.put(self._PriorityEvent(
                    priority=priority, event=event))
                self._condition.notify()

        def dequeue(self):
            with self._condition:
                while self.is_empty():
                    self._condition.wait()
                return self._queue.get()

        def is_empty(self):
            return self._queue.empty()

        def flush(self):
            while not self._queue.empty():
                self._queue.get()

        @ dataclass(order=True)
        class _PriorityEvent:
            """Will compare _PriorityItems based on the priority field and not the event field"""
            event: typing.Any = field(compare=False)
            priority: int = 3

    class _Runner(threading.Thread):
        def __init__(self, events_queue):
            super().__init__()
            """Will continuouly dequeue events from _EventsQueue and run the function that
            is requested in the event then emit any results produced on the signal that was specifed
             by the service that requested the event"""
            self.events_queue = events_queue
            self._is_running = True
            self._stop_lock = threading.Lock()

        def is_running(self):
            return self._is_running

        def run(self):
            print("Starting DataDecision Runner")
            while self.is_running():
                try:
                    priority_event = self.events_queue.dequeue()
                    event = priority_event.event

                    if event:
                        print(
                            f"DataDecision is running an event {event}")

                        event.run()

                except Exception as e:
                    print(
                        f"ERROR {e} occured when _Runner tried to emit {event} event")
            print("DataDecision End")

        def stop(self):
            with self._stop_lock:
                self._is_running = False
                self.events_queue.enqueue(event=None, priority=1)
