import cv2
import multiprocessing as mp
import time

import atexit

def _opencv_capture(target_url, stop_flag, frame_queue: mp.Queue):
    cap = cv2.VideoCapture(target_url)

    while not stop_flag.value:
        ret, frame = cap.read()

        if frame_queue.empty():
            frame_queue.put(frame)
    cap.release()


class StreamReceiver(object):
    def __init__(self, url, port, processing_method ='fork'):
        base_url = 'udp://{address}:{port}'
        base_url = base_url.format(address=url, port=port)
        self._url = base_url

        self._stop_flag = mp.Value('i', False)

        self._frame_queue = mp.Queue()
        self._ctx = mp.get_context(processing_method)

        self._recv_callback = None
        atexit.register(self.close)

    def set_recv_callback(self, recv_callback):
        self._recv_callback = recv_callback

    def open(self):

        if not self._recv_callback:
            raise ReferenceError('recv_callback is None. Please define with set_recv_callback().')

        cap_proc = self._ctx.Process(target=_opencv_capture, args=(self._url, self._stop_flag, self._frame_queue))
        cap_proc.start()

        while not self._stop_flag.value:
            frame = self._frame_queue.get()

            self._recv_callback(self, frame)

            while not self._frame_queue.empty():
                self._frame_queue.get()
        print('waiting for other process.')
        cap_proc.join()
        self._stop_flag.value = False

    def close(self):

        self._stop_flag.value = True


if __name__ == '__main__':
    test = StreamReceiver('localhost', 8888)

    def test_callback(streamer, frame):
        time.sleep(0.3)
        cv2.imshow('test', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('hit!')
            streamer.close()
            cv2.destroyAllWindows()

    test.set_recv_callback(test_callback)
    test.open()