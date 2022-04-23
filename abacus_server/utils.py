from threading import Timer


class RepeatingTimer(Timer):
    """Will repeatedly call a function at a set interval.
        Args:
            interval: float      number of seconds between function calls
            function: function   name of function to be repeatedly called
            timer_name: str      name to describe timer
            arg/kwargs           parameters to be passed to the function getting called

        Returns:
            the results of the function being called    
        """

    def __init__(self, interval: float, function, timer_name: str = 'RepeatingTimer', *args, **kwargs):
        super().__init__(interval, function)
        self.args = args
        self.kwargs = kwargs
        self.function = function
        self.interval = interval
        self.name = timer_name

    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            # c= Console()
            # c.print("Timer Finished ", style='underline red on white')
            self.function(*self.args, **self.kwargs)
        self.finished.set()
