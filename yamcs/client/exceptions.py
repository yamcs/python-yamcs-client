class ConnectionError(Exception):
    def __init__(self, message='', reply=None):
        super(ConnectionError, self).__init__(message)
        self.reply = reply
