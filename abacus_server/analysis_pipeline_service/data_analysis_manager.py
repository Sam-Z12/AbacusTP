import random
import threading
from pydantic import validate_arguments
from concurrent.futures import ProcessPoolExecutor

from ..global_events import global_events_manager
from ..models.analysis_pipeline_models import DataAnalysisInput, DataDecisionInput


class DataAnalysisManager:
    def __init__(self, input_signal: str = "data_source_manager", output_signal: str = "data_analysis_manager") -> None:
        self.input_signal = input_signal
        global_events_manager.connect(
            self.receiver, self.input_signal)

        self._output_signal = output_signal
        global_events_manager.add_signal(self._output_signal)

        self._data_analyses = {}
        self.executor = ProcessPoolExecutor(max_workers=2)
        self.active_futures = self._UniqueDict()
        self.finished_futures = self._LockingQueue()
        self.results = self.Resulter(
            self.finished_futures, self.active_futures, self._output_signal)
        self.results.start()

    @validate_arguments
    def receiver(self, sender, signal, message: DataAnalysisInput):
        """Will recieve and validate data then send data to data_analysis_manager"""
        # print(self.data_analyses)

        print(f"DataAnalysis Recieved a message from {sender}")

        try:
            message = message.dict()
            print(f"ANALYSIS INPUT MESSAGE {message}")

            name_tag = message["name_tag"]

            if self.is_bypassed(message):
                message.update({"analysis_results": "in_bypass"})
                global_events_manager.send_signal(
                    service_name=self._output_signal, sender=name_tag, message=message)

            else:
                data_analysis_obj = self._data_analyses.get(name_tag)
                print(f"ANALYSIS OBJ DICT: {self._data_analyses}")
                print(f"ANALYSIS OBJ: {data_analysis_obj}")
                self.deposit(data_analysis_obj.run, message)

        except Exception as e:
            print(
                f"ERROR: {e}... analysis reciever could interpet incoming signal from {sender}")

    def runner(self, analysis_name, input):
        """analysis_name should be the same as the sender parameter 
        received in receiver and the name_tag parameter of the message dict"""
        try:
            analysis_func = self.data_analyses[analysis_name]

        except Exception as e:
            print(e,
                  f"ERROR: {e} data analysis runner could not run {analysis_name} function")
        return analysis_func.run(input=input)

    def append_data_analysis(self, data_analysis):
        try:
            data_analysis_name = data_analysis.name_tag
            self._data_analyses.update({data_analysis_name: data_analysis})
        except Exception as e:
            print(f"ERROR {e} Could not add {data_analysis}")

    def remove_data_analysis(self, data_analysis_name):
        try:
            self._data_analyses.pop(data_analysis_name)

        except Exception as e:
            print(f"ERROR {e} Could not remove {data_analysis_name}")

    def append_multiple_data_analyses(self, list_of_analyses):
        for a in list_of_analyses:
            self.append_data_analysis(a)

    def is_bypassed(self, data_source_message):
        try:
            return data_source_message['function_params']['analysis_bypass']
        except Exception as e:
            print(
                f"ERROR: {e} Could not find analysis bypass in message {data_source_message}")
            return True

    def active_futures_count(self):
        return len(self.active_futures)

    def deposit(self, fn, message):
        """Submits fn to the ProcessPool Executor. Executor will try to pickle an fn when it is submitted. Trying to submit a reference 
        to a function that has already been submitted (i.e. submitting the same function twice) 
        will result in a pickling error and the function will not be run."""
        unique_item = self.active_futures.update(fn, message)
        future = self.executor.submit(unique_item)
        future.add_done_callback(self._future_done_callback)
        print(
            f"Added fn to Executor there is now {self.active_futures_count()} process active")

    def _future_done_callback(self, future):
        try:
            if future.done():
                self.finished_futures.enqueue(future)
                print(f"{future} finished running")
            else:
                print(f"{future} did not finish but got done call back")

        except Exception as e:
            print(
                f"ERROR {future} finished but could not bet added to the finished futures queue")

    def terminate(self):
        """Ends all threads and processes. 
            Will wait for all analyses that are currently being processed to compelete running"""
        self.results.stop()
        self.executor.shutdown(wait=True)
        # self.finished_futures.end_wait()

    def kill(self):
        """Will end all analysis threads and processes even if they are currently being run"""
        self.results.stop()
        self.executor.shutdown(wait=False)
        # self.finished_futures.end_wait()

    class _UniqueDict:
        def __init__(self) -> None:
            self._dict = {}
            self.max_size = 10000
            self._condition = threading.Condition()

        def __len__(self):
            with self._condition:
                return len(self._dict)

        def update(self, fn, message):
            with self._condition:
                if len(self) >= self.max_size:
                    print("Unique dictionary is full. Can not add new item")
                    return False
                else:
                    item = self._RandomItem(fn, message, self)
                    while item.id in self._dict:
                        item = self._RandomItem(fn, message, self)

                    self._dict.update({item.id: item})
                    return item

        def pop(self, key):
            with self._condition:
                return self._dict.pop(key)

        def get(self, key):
            with self._condition:
                return self._dict.get(key)

        def dict(self):
            with self._condition:
                return self._dict

        def check_hashes(self):
            with self._condition:
                hashes = []
                for item in self._dict.values():
                    h = hash(item)
                    if h not in hashes:
                        hashes.append(h)
                    else:
                        print("ERROR dict is not Unique")
                        return False
                print("dict is unique")
                return True

        class _RandomItem(object):
            def __init__(self, fn, message, dict) -> object:
                """Ensures that an item added to the dict is unique according to its hash. 
                This is achieved by creating a random id then checking if an item with the same id is already in the dict.
                It will continue creating a new item until the id is unique"""
                self.fn = fn
                self.message = message
                self.dict_len = len(dict)
                self.id = random.randint(0, self.dict_len * 2)

            def __call__(self):
                return self.id, self.fn(self.message)

    class _LockingQueue:
        """Finish futures will be added to a queue and wait to be called."""

        def __init__(self) -> None:
            self._queue = []
            self._condition = threading.Condition()

        def is_empty(self):
            return len(self._queue) == 0

        def enqueue(self, finished_future):
            with self._condition:
                self._queue.append(finished_future)
                self._condition.notify()

        def dequeue(self):
            with self._condition:
                while self.is_empty():
                    self._condition.wait()

                return self._queue.pop(0)

        def end_wait(self):
            with self._condition:
                while self.is_empty():
                    self._condition.notify()

    class Resulter(threading.Thread):
        def __init__(self, queue, active_futures, output_signal):
            """Thread which will try to keep calling dequeue 
                on the finished futures list. Will get the 
                future result and send results"""
            super().__init__()
            self.queue = queue
            self.active_futures = active_futures
            self.output_signal = output_signal
            self._is_running = True
            self._stop_lock = threading.Lock()

        def run(self):

            while self._is_running:
                try:
                    finished_future = self.queue.dequeue()

                    if finished_future:
                        result = finished_future.result()
                        analsis_id = result[0]
                        analysis_result = result[1]
                        print(f" Runner got {result}")

                        # item will contain the original message that envoked this future to run
                        item = self.active_futures.pop(analsis_id)
                        envoking_message = item.message
                        analysis_name = envoking_message['name_tag']
                        envoking_message.update(
                            {"analysis_results": analysis_result})
                        global_events_manager.send_signal(
                            service_name=self.output_signal, sender=analysis_name, message=envoking_message)

                        print(f"{analysis_name} analysis finished running")

                except Exception as e:
                    print(
                        f"ERROR {e} occured when _Runner tried to emit  event")
            print("Data Analysis Ended")

        def stop(self):
            with self._stop_lock:
                self._is_running = False
                self.queue.enqueue(finished_future=None)
