# vim: ts=4:sw=4
class Raised():
    def __init__(self, exception, message, condition):
        self.exception = exception
        self.message = message
        self.condition = condition
