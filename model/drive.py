from .base import BaseModel


class DriveModel(BaseModel):
    def __init__(self, remote_controller):
        super(DriveModel, self).__init__(remote_controller)

    def main(self, remote_controller, stream_receiver, frame):
        pass

