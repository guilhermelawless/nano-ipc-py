class IPCError(Exception):
    pass


class ConnectionFailure(IPCError):
    pass


class ConnectionClosed(IPCError):
    pass


class BadRequest(IPCError):
    pass


class BadResponse(IPCError):
    def __init__(self, message, response_raw):
        super().__init__(self, message)
        self.response_raw = response_raw
        self.message = message
