import asyncio
import pickle as pk
import multiprocessing as mp


def _event_loop_run(io_handle, url, port):
    event_loop = asyncio.get_event_loop()
    async_start = asyncio.start_server(io_handle, url, port, loop=event_loop)
    event_loop.run_until_complete(async_start)
    event_loop.run_forever()


class RemoteController(object):

    class Command(object):
        def __init__(self, size):
            self._data = bytearray(size)

        def __call__(self, to_serialize):
            if not to_serialize:
                return

            if type(to_serialize) not in [dict, list, tuple]:
                raise ValueError('Command data only support dict, list, tuple.')

            dumped = pk.dumps(to_serialize)

            if len(dumped) > len(self._data):
                raise ValueError('Too big to dump. Object must have less then {} bytes.'.format(len(self._data)))
            self._data = dumped

            return self

        def raw(self):
            return self._data

    def __init__(self, url, port, statbytes = 3):
        self._url = url
        self._port = port
        self._statbytes = statbytes
        self._server = None
        self._proc = None
        self._command_queue = mp.Queue()
        self._ctx = mp.get_context('fork')

    def start(self):
        self._proc = self._ctx.Process(target=_event_loop_run, args=(self._io_handle, self._url, self._port))
        self._proc.start()

    def stop(self):
        self._proc.join()

    def push_command(self, cmd):
        if self._command_queue.full():
            while not self._command_queue.empty():
                self._command_queue.get()
        self._command_queue.put(cmd)

    async def _io_handle(self, reader, writer):
        while True:
            data = await reader.read(128)
            cmd_builder = self.Command(self._statbytes)

            result = cmd_builder([0, 1, 0]) if self._command_queue.empty() else self._command_queue.get()

            if type(result) is not self.Command:
                raise RuntimeError('Invalid Command Error.')

            raw = result.raw()
            writer.write(raw)
            await writer.drain()

if __name__ == '__main__':
    remote_controller = RemoteController('0.0.0.0', 8888, 32)

    remote_controller.start()

    while True:
        remote_controller.push_command(remote_controller.Command([0, 1, 0]))
