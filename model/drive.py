from .base import BaseModel

from lib.alexnet import alexnet
import cv2

class DriveModel(BaseModel):
    def __init__(self, remote_controller):
        super(DriveModel, self).__init__(remote_controller)
        WIDTH = 160
        HEIGHT = 120
        LR = 1e-3
        EPOCHS = 10
        MODEL_NAME = './lib/pygta5-car-fast-{}-{}-{}-epochs-300K-data.model'.format(LR, 'alexnetv2', EPOCHS)
        t_time = 0.09
        self.model = alexnet(WIDTH, HEIGHT, LR)
        self.model.load(MODEL_NAME)

    def main(self, remote_controller, stream_receiver, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        frame = cv2.resize(frame, (160, 120))
        prediction = self.model.predict([frame.reshape(160,120,1)])[0]

        # turn_thresh = 0.7
        # fwd_thresh = 0.
        #
        # if prediction[1] > fwd_thresh:
        #     vec = [0, 1, 0]
        #     cmd = remote_controller.Command(32)
        #
        # elif prediction[0] > turn_thresh:
        #     vec = [1, 0, 0]
        #     cmd = remote_controller.Command(32)
        # elif prediction[2] > turn_thresh:
        #     vec = [0, 0, 1]
        #     cmd = remote_controller.Command(32)
        # else:
        #     vec = [0, 1, 0]
        #     cmd = remote_controller.Command(32)

        prediction = prediction.tolist()
        vec = [0, 0, 0]
        max_index = prediction.index(max(prediction))

        vec[max_index] = 1
        cmd = remote_controller.Command(32)

        remote_controller.push_command(cmd(vec))
        return