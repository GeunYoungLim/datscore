import argparse
import cv2

from server.control import RemoteController
from server.stream import StreamReceiver
from model.drive import DriveModel
from model.objectdetect import DetectionModel

import multiprocessing as mp


def driving_ai_logic(config):
    rc = RemoteController(config.service, config.vision, 32)
    rc.start()

    model = DriveModel(rc)

    sr = StreamReceiver(config.service, config.ctrl)
    sr.set_recv_callback(model.predict)
    sr.open()


def object_detaction_logic(config):
    rc = RemoteController(config.service, config.obj, 32)
    rc.start()

    model = DetectionModel(rc)

    sr = StreamReceiver(config.service, config.react)

    sr.set_recv_callback(model.predict)
    sr.open()


if __name__ == '__main__':

    args = argparse.ArgumentParser()
    args.add_argument('--service', type=str, default='0.0.0.0')
    args.add_argument('--vision', type=str, default='9000')
    args.add_argument('--ctrl', type=str, default='8000')
    args.add_argument('--obj', type=str, default='9900')
    args.add_argument('--react', type=str, default='8800')
    config = args.parse_args()

    ctx = mp.get_context('fork')
    driving_ai_process = ctx.Process(target=driving_ai_logic, args=(config,))
    object_detection_process = ctx.Process(target=object_detaction_logic, args=(config,))
    driving_ai_process.start()
    object_detection_process.start()
