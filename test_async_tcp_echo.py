import unittest
import socket
from random import choice
from string import ascii_lowercase
from async_tcp_echo_serv import AsyncTCPEchoServ, TCPSocket, PORT, RECV_BUFFER, MAX_CONN


class TestTCPClient(TCPSocket):

    def __init__(self, host='localhost', port=PORT):
        super(TestTCPClient, self).__init__()
        self.connect((host, port))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def receive(self, buff):
        data = self.recv(buff)
        print('Received:', data)
        return data


# fixtures
full_line = b'Hello there\n' 
big_line = bytes(''.join([choice(ascii_lowercase) for _ in range(2047)]) + '\n',
	             'utf-8')


class TestAsyncTcpEchoServ(unittest.TestCase):

    def __init__(self, arg):
      super(TestAsyncTcpEchoServ, self).__init__(arg)

    def test_send_fullline(self):
        with TestTCPClient() as test_tcp_client:
            test_tcp_client.sendall(full_line)
            data = test_tcp_client.receive(RECV_BUFFER)
            self.assertEqual(full_line, data)

    def test_send_not_fullline(self):
        data = TestAsyncTcpEchoServ.__send_line_parts()
        self.assertEqual(full_line, data)

    def test_max_conn_send_not_fullline(self):
        """About testing MAX_CONN simultaneous connections"""
        for _ in range(MAX_CONN):
            data = TestAsyncTcpEchoServ.__send_line_parts()
            self.assertEqual(full_line, data)

    def test_send_big_line(self):
        """About transferring bytestrings larger than RECV_BUFFER,
           but smaller than RECV_BUFFER*2"""

        with TestTCPClient() as test_tcp_client:
            test_tcp_client.sendall(big_line)
            data = b''
            data_len = 0

            while not (data_len == len(big_line)):
                 data += test_tcp_client.receive(RECV_BUFFER)
                 data_len = len(data)
            self.assertEqual(big_line, data)

    def __send_line_parts():
        with TestTCPClient() as test_tcp_client:
            test_tcp_client.sendall(full_line[:-6])
            test_tcp_client.sendall(b'there\n')
            return test_tcp_client.receive(RECV_BUFFER)

    # TODO fix RECV_BUFFER*2 bytestrings (will fix w/ select's writables and queues?)

if __name__ == '__main__':
    with unittest.main() as main: pass