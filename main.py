import argparse
import cv2

from server.control import RemoteController
from server.stream import StreamReceiver



if __name__ == '__main__':
    args = argparse.ArgumentParser()

    args.add_argument('--stream', type=str, default='0.0.0.0:9000')
    args.add_argument('--control', type=str, default='0.0.0.0:8000')

    config = args.parse_args()
    stream_url, stream_port = config.stream.split(':')
    control_url, control_port = config.control.split(':')

    rc = RemoteController(control_url, control_port, 32)
    rc.start()


    def recv_callback(stream_receiver, frame):
        rc.push_command(rc.Command([0, 1, 0]))
        print('frame', frame.shape)
        cv2.imshow('test', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('hit!')
            stream_receiver.close()
            cv2.destroyAllWindows()
            sr.close()

    sr = StreamReceiver(stream_url, stream_port)

    sr.set_recv_callback(recv_callback)
    sr.open()