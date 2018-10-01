from .base import BaseModel


class DetectionModel(BaseModel):
    def __init__(self, remote_controller):
        super(DetectionModel, self).__init__(remote_controller)

    def main(self, remote_controller, stream_receiver, frame):
        pass

