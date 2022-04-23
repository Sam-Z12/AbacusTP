import typing
import queue
import threading
from pathlib import Path
from pydispatch import dispatcher
from pydantic import validate_arguments
from dataclasses import dataclass, field

from .api_clients import crypto_client
from ..models.data_request_models import ApiDataRequest, ApiDataRequestRespone
from ..global_events import global_events_manager


class CryptoServiceEventsManager:
    """Interface that will recive signals sent with the name of the paren_dir<analysis_pipeline_service>_sig aka: crypto_service_sig.
        Signals are interpeted by the reciever() function which will check if the signal is trying to set up a websocket connection or make an api
        https request. Https request can be either reoccuring or a one time call. If recall_interval is None a one time call is made where the reciever
        creates an event and adds the event to the events_queue. If a recall_interval is specified the reciever will create a new event then wrap
        the event in a _ReoccuringEvent that will repeatedly add that event to the event queue every <recall_interval> seconds. _ReoccuringEvents are
        kept track of in the reoccuring_events_dict. A _Runner class thread will continuously remove events from the events_queue and try calling the
        event.emit() function which calls a target_fucntion of the api client and emits a signal containing the results of the target_function with a signal
        name <sender>.




    TODO: Make _Event a data_class cand get rid of _PriorityItem.

    """

    def __init__(self, clients: dict = {"crypto_client": crypto_client}) -> None:
        self.name_tag = "crypto_service"
        self.clients = clients
        self.crypto_cli = self.clients['crypto_client']
        print(f"CLI {self.clients}")
        parent_dir_name = Path(__file__).parent.name
        dispatcher.connect(self.reciever, signal=f'{parent_dir_name}_sig',
                           sender=dispatcher.Any)
        self.events_queue = self._EventQueue()
        self.runner = self._Runner(events_queue=self.events_queue)
        self.runner.start()

    @validate_arguments
    def reciever(self, sender, signal, message: ApiDataRequest):
        """Will validate incoming signals, parse data, create event, and add event to queue
            Need to add option for client name and remove event"""
        print(f"Crypto Service recieved an event from {sender}")
        print(f"MESSAGE: {message}")
        message_dict = message.dict()
        try:
            if message_dict['type'] == "https":
                target_function = message_dict['target_function']
                print(f"Crypto Service Target Function: {target_function}")
                print(self.clients)
                new_event = self._Event(
                    sender=sender, target_function=target_function, client=self.crypto_cli)
                self.events_queue.enqueue(new_event)
            elif message_dict['type'] == 'websocket':
                print('Support for Websocket Events coming soon')

            """Try using hash table to keep track of what to do at each point"""

        except Exception as e:
            print(
                f"Error {e} occured when crypto service tried to interpret message from {sender}")

    def queue_size(self):
        return len(self.events_queue)

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

    @dataclass
    class _Event:
        """An event creates a RepeatingTimer that recalls a target_function at a given time interval.
            After the function is called a signal with name f"{sender}_sig" is emited. This signal
            contains the results of the target function.

        Args:
            sender: str                 Will be the name of the function/DataSource which is requesting the event
            target_function: function   Name of the function to be called. dictionary that would contain kwargs as well.
            client: client for an api exp. Coinbase_Pro_Client
        """

        def __init__(self, sender, target_function, client):

            self.sender = sender
            self.target_function = target_function
            self.client = client
            self.name = sender + ":" + target_function['name']

        def emit(self, sender_name):
            """Retrieves and runs the target function then emits the results."""
            target_function = self.client.__getattribute__(
                self.target_function['name'])

            def _run_target_func(function, **kwargs):
                return function(**kwargs)
            results = _run_target_func(function=target_function, **
                                       self.target_function['kwargs'])

            results = {self.target_function['name']: results}
            #print(f"CRYPTO SERVICE RESULTS: {results}")

            print(f"Crypto Service sending {self.sender}_sig")
            global_events_manager.emit_signal(reciever=self.sender, sender=sender_name, message=ApiDataRequestRespone(
                name_tag=self.sender, content=results, tf_params=self.target_function))

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
            print("Starting CytpyoService Runner")
            while self.is_running():
                try:
                    priority_event = self.events_queue.dequeue()
                    event = priority_event.event

                    if event:
                        print(
                            f"Crypto Service is running an event {event.name}")
                        event.emit(sender_name="crypto_service")
                        print(
                            f"Crypto Service is emmiting an event {event.name}")
                except Exception as e:
                    print(
                        f"ERROR {e} occured when _Runner tried to emit {event} event")
            print("Cryto Runner End")

        def stop(self):
            with self._stop_lock:
                self._is_running = False
                self.events_queue.enqueue(event=None, priority=1)


#interface = CryptoServiceEventsManager()
