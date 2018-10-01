
class BaseModel(object):
    def __init__(self, remote_controller):
        self._rc = remote_controller

    def predict(self, stream_receiver, frame):
        self.main(self._rc, stream_receiver, frame)

    def main(self, remote_controller, stream_receiver, frame):
        raise NotImplementedError('You must implement this method in subclass.')