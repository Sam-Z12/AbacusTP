
import os
import queue
import threading
from typing import Any
from dataclasses import dataclass, field
from pydantic import validate_arguments

from ..global_events import global_events_manager
from ..models.data_request_models import ApiDataRequest, ApiDataRequestRespone
from ..models.analysis_pipeline_models import DataAnalysisInput
from ..utils import RepeatingTimer


class DataSourceManager:
    def __init__(self, name: str = "data_source_manager"):
        """Will recieve all signals from services which are polling different DataSources.

            Filepaths for the data_source files are found based on a relative path below.

            Args:
                signal_name: str    this is the channel which other services can send DataSourceManager signals at.

        """
        self._is_online = True
        self.signal_name = name
        self._output_signal_name = None
        global_events_manager.add_signal(self.signal_name)
        #global_events_manager.connect(self.receiver, self.signal_name)

        self._events_queue = self._EventQueue()
        self.data_sources_dictionary = {}
        self.runner = self._Runner(self._events_queue)
        self.runner.start()

    @validate_arguments
    def receiver(self, sender, signal, message: ApiDataRequestRespone):
        """Will recieve and validate data then send data to data_analysis_manager
        """
        print(f"Datasource Recieved a message from {sender}")

        try:
            message = message.dict()
            print(
                f"DATASOURCE MESSAGE {message}, Signal {signal}, Sender {sender}")

            print(
                f"DataSourceManger data source dictionary: {self.data_sources_dictionary}")
            # This will be the name of the DataSource which asked for a request
            name_tag = message['name_tag']

            # Find the original function parameters from the DataSource object and send the down the pipeline in the response.
            # Analysis bypass parameter can be used by DataAnalysis manager.
            function_name = list(message['content'].keys())[0]
            print(f"FUNCTION {function_name}")

            # Set defualt funtion params in case the function name can't be found in data_sources
            function_params = {"default": "error_no_function_params"}
            for func in self.data_sources_dictionary[name_tag].data_source.target_functions:
                print(f"FUNCS IN DS {func['name']}")
                if str(func['name']) == str(function_name):
                    function_params = func

            print("Enqueuing data results to send to data analysis")
            new_data_source_relay_event = self._DataSourceRelayEvent(
                signal_name=self.signal_name, name_tag=name_tag, source_results=message['content'], function_params=function_params)

            self._events_queue.enqueue(
                event=new_data_source_relay_event, priority=3)
        except Exception as e:
            print(
                f"Error: {e} data_source_manager could not interpet message from {sender}")

    def start(self):
        self._is_online = True

    def terminate(self):
        """stop runner and deactivate all repeating events"""
        self.deactivate_all()
        self.runner.stop()
        self._is_online = False

    def data_source_count(self):
        return len(self.data_sources_dictionary)

    def append_data_source(self, data_source):
        """
        for each target_function in data source create an event
        add event to repeater if recall interval
        add repeating events to the repeating event dict
        create data_source_container
        add repeating event dict to the data source container
        add data_source_container to data_source_dictionary
        """
        try:
            self._create_data_source_port(data_source=data_source)
            data_source_name = data_source.name_tag
            target_service = data_source.service_name
            data_source_repeating_event_dict = self._RepeatingEventsDict()
            for tf in data_source.target_functions:
                new_data_request_event = self._DataRequestEvent(
                    data_source_name=data_source_name, target_function=tf, target_service_name=target_service, client="", type="https")
                if tf['recall_interval']:
                    repeating_data_request_event = self._EventRepeater(
                        event=new_data_request_event, recall_interval=tf['recall_interval'], queue=self._events_queue)
                    data_source_repeating_event_dict.add_repeating_event(
                        repeating_data_request_event)
                else:
                    self._events_queue.enqueue(
                        event=new_data_request_event, priority=3)
            data_source_container = self._DataSourceContainer(
                data_source=data_source, repeating_events=data_source_repeating_event_dict, is_active=True)
            self.data_sources_dictionary.update(
                {data_source_name: data_source_container})

        except Exception as e:
            print(f"ERROR Could not add {data_source}")

    def append_multiple_data_sources(self, data_sources: list):
        for data_source in data_sources:
            self.append_data_source(data_source)

    def remove_data_source(self, data_source_name):
        try:
            data_source_container = self.data_sources_dictionary[data_source_name]
            repeating_events_dict = data_source_container.repeating_events
            for repeating_event in repeating_events_dict:
                repeating_events_dict[repeating_event].cancel()
            self.data_sources_dictionary.pop(data_source_name)
        except Exception as e:
            print(f"ERROR Could not remove {data_source_name}")

    def deactive_data_source(self, data_source_name):
        try:
            data_source_container = self.data_sources_dictionary[data_source_name]
            repeating_events_dict = data_source_container.repeating_events
            for repeating_event in repeating_events_dict:
                repeating_events_dict[repeating_event].cancel()
            data_source_container.is_active = False
        except Exception as e:
            print(f"ERROR Could not deactivate {data_source_name}")

    def activate_data_source(self, data_source_name):
        try:
            data_source_container = self.data_sources_dictionary[data_source_name]
            if not data_source_container.is_active:
                repeating_events_dict = data_source_container.repeating_events
                for repeating_event in repeating_events_dict:
                    repeating_events_dict[repeating_event].activate()
                data_source_container.is_active = True
            else:
                print(f"ERROR {data_source_name} is already active")
        except Exception as e:
            print(f"ERROR failed to activate {data_source_name}")

    def deactivate_all(self):
        for data_source_name in self.data_sources_dictionary:
            self.deactive_data_source(data_source_name)

    def activate_all(self):
        for data_souce_name in self.data_sources_dictionary:
            self.activate_data_source(data_souce_name)

    def _create_data_source_port(self, data_source):
        try:
            global_events_manager.add_signal(data_source.name_tag)
            global_events_manager.connect(self.receiver, data_source.name_tag)
        except Exception as e:
            print(f"ERROR Could not create a port for {data_source}")

    def delete_data_source_port(self, data_source):
        pass

    def queue_size(self):
        return len(self._events_queue)

    @dataclass
    class _DataSourceContainer:
        data_source: Any
        repeating_events: Any
        is_active: bool = False

    class _RepeatingEventsDict:
        """This will be filled with timers that will repeatedly add events into the events queue after a specified amount of time.
            These are used to poll specific end points of apis. Need to have a max size function so dict does not grow indefinately"""

        def __init__(self, max_events=50) -> None:
            self.max_events = max_events
            self._dict = {}

        def __add__(self, event_repeater):

            self.add_repeating_event(event_repeater=event_repeater)

        def __len__(self):
            return len(self._dict)

        def __iter__(self):
            for key in self._dict:
                yield key

        def __getitem__(self, key):
            return self._dict[key]

        def add_repeating_event(self, event_repeater):

            if len(self._dict) > self.max_events:
                print(
                    "Cannot add event,the repeating events dict already contains the max amount of events")
            else:
                # events are addressed acording to the sender name.
                event_name = event_repeater.event_name
                self._dict.update({event_name: event_repeater})

        def remove_event(self, event_repeater_name):
            self._dict.pop(event_repeater_name)

        def active_events(self):
            return self._dict

    class _EventRepeater:

        def __init__(self, event, recall_interval, queue, priority: int = 3) -> None:
            """Creates a RepeatingTimer that continuously adds an event to the event_queue every <recall_interval> seconds.
                Just wraps an _Event in a repeating timer.

            Args:
                sender: str                 Will be the name of the function/DataSource which is requesting the event
                interval: int               Number of seconds between how often the event occurs
                target_function: function   Name of the function to be called
            """
            self.event = event
            self.recall_interval = recall_interval
            self.queue = queue
            self.priority = priority
            self.timer = RepeatingTimer(
                interval=self.recall_interval, function=self.enqueue_event)
            self.enqueue_event()
            self.timer.start()

        def enqueue_event(self):
            self.queue.enqueue(event=self.event,
                               priority=self.priority)

        def cancel(self):
            """Will cancel the reoccuring event"""
            self.timer.cancel()

        def activate(self):
            if not self.timer.is_alive:
                self.timer.start()
            else:
                print(f"ERROR {self.event.event_name} is already active")

    class _DataSourceRelayEvent:
        def __init__(self, signal_name, name_tag, source_results, function_params) -> None:
            self.signal_name = signal_name
            self.name_tag = name_tag
            self.source_results = source_results
            self.function_params = function_params

        def emit(self):
            message = DataAnalysisInput(
                name_tag=self.name_tag, source_results=self.source_results, function_params=self.function_params)
            # Signal name with just keep sending events to this reciever and create a loop
            global_events_manager.emit_signal(
                reciever=self.signal_name, sender=self.name_tag, message=message)

    class _DataRequestEvent:
        """An event creates a RepeatingTimer that recalls a target_function at a given time interval.
            After the function is called a signal with name f"{sender}_sig" is emited. This signal
            contains the results of the target function.

        Args:
            sender: str                 Will be the name of the function/DataSource which is requesting the event
            target_function: function   Name of the function to be called. dictionary that would contain kwargs as well.
            client: client for an api exp. Coinbase_Pro_Client
        """

        def __init__(self, target_function, data_source_name, target_service_name, client, type) -> None:

            self.target_function = target_function
            self.data_source_name = data_source_name
            self.target_service_name = target_service_name
            self.client = client
            self.type = type
            self.event_name: str = self.data_source_name + \
                ":" + self.target_function['name']

        def emit(self):
            """Retrieves and runs the target function then emits the results."""
            # message = {"client": self.client, "type": self.type, "target_function": {
            #     "name": self.target_function['name'], "kwargs": self.target_function['kwargs']}, "recall_interval": self.target_function['recall_interval']}

            message = ApiDataRequest(
                client=self.client, type="https", target_function=self.target_function)

            global_events_manager.send_signal(
                service_name=self.target_service_name, sender=self.data_source_name, message=message)

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
            """Will compare _PriorityItems based on the priority field and not the item field"""
            event: Any = field(compare=False)
            priority: int = 3

    class _Runner(threading.Thread):
        def __init__(self, events_queue):
            super().__init__()
            """Will continuouly dequeue events from _EventsQueue and run the function that
            is requested in the event then emit any results produced on the signal that was specifed
             by the service the requested the event"""
            self.events_queue = events_queue
            self._is_running = True
            self._stop_lock = threading.Lock()

        def is_running(self):
            return self._is_running

        def run(self):
            print("Starting DataSourceManager Runner")
            while self.is_running():
                try:
                    priority_event = self.events_queue.dequeue()
                    event = priority_event.event
                    print(f"DataSourceManager is running an event")
                    if event:
                        event.emit()
                except Exception as e:
                    print(
                        f"ERROR {e} occured when _Runner tried to emit {event} event")
            print("Data Soource ended")

        def stop(self):
            with self._stop_lock:
                self._is_running = False
                self.events_queue.enqueue(event=None, priority=3)
                # self.events_queue._condition.notify()
