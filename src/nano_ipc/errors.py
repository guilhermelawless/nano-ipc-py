class ConnectionClosed(Exception):
    pass


class BadRequest(Exception):
    pass


class BadResponse(Exception):
    def __init__(self, message, response_raw):
        super().__init__(self, message)
        self.response_raw = response_raw
        self.message = message
