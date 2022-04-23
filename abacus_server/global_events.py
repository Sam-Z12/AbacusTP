import os
from os import path
from pydispatch import dispatcher

"""
Build model for a signal to garentee signals
being send are valid/ all contain the same schema.
All events should share the same schema!!!!"""


class SignalBody:
    body: dict


class Test:
    def __init__(self) -> None:
        print("asdfasdf")

    def printer(self):
        print("iniasdkfjaskdjf")


class EventsManager:

    def __init__(self) -> object:
        """
            Returns:
                list: contains a list of signals available to connect to
        """
        self.signals = self._service_signal_list()

    def _service_signal_list(self):
        """Used to create the intial default signals used for 
            services to communicate between each other.

            The abacus_server packages is parsed and any directory 
            containing service in the name will have a default signal 
            created with the titile following the schema {directory name}_sig. 
            """
        parent_dir = path.dirname(__file__)
        signals = []
        for file in os.listdir(parent_dir):
            if "service" in file:
                SIGNAL = f"{file}_sig"
                signals.append(SIGNAL)
                print(f"{file} is a service")
        print(signals)
        return signals

    def emit_signal(self, reciever: str, sender: str, message):
        """
        copy of send signal but with differnt terminology"""

        sig_name = f"{reciever}_sig"

        if sig_name in self.signals:
            print(f"Sending {reciever}_sig ...")
            dispatcher.send(signal=sig_name, sender=sender, message=message)

        else:
            raise KeyError(f'{reciever}_sig does not exist')

    def send_signal(self, service_name: str, sender, message):
        """
        Used to send signals between the services in the abacus_server package.
        Verifies that the signal trying to be sent exists"""

        sig_name = f"{service_name}_sig"

        if sig_name in self.signals:
            print(f"Sending {service_name}_sig ...")
            dispatcher.send(signal=sig_name, sender=sender, message=message)

        else:
            raise KeyError(f'{service_name}_sig does not exist')

    def add_signal(self, name: str):
        """Used to add new signal channels to EventsManager.
            Will take care of creating the name of the signal with the correct schema"""
        sig_name = f"{name}_sig"
        self.signals.append(sig_name)

    def connect(self, handler_func: str, name: str, sender=dispatcher.Any):
        if f"{name}_sig" in self.signals:
            dispatcher.connect(receiver=handler_func,
                               signal=f"{name}_sig", sender=dispatcher.Any)
        else:
            raise KeyError(f'{name}_sig does not exist')


global_events_manager = EventsManager()


"""
Message Request data from data source should follow the schema

{
    type: str   can be "https" or "websocket"
    func: str   name of the fuction/api call that should be called
    interval: int   time in (secs) between updates. Websockets ignore this field 
}


"""
