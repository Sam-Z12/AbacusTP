from abacus_server.global_events import global_events_manager


def test_global_event():

    class Connection:

        def __init__(self) -> object:

            self.hi_message = "hi"
            self.signal_name = "test"
            self.was_reciever_called = False
            global_events_manager.add_signal(self.signal_name)
            global_events_manager.connect(self.reciever, self.signal_name)
            self.sender(message=self.hi_message, signal_name=self.signal_name)

        def reciever(self, sender, signal, message):
            assert message == self.hi_message
            self.was_reciever_called = True

        def sender(self, message, signal_name):
            global_events_manager.send_signal(
                signal_name, sender="sender", message=message)

    c = Connection()
    assert c.was_reciever_called == True
