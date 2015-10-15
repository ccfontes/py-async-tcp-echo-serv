import socket
from select import select

PORT = 30000
RECV_BUFFER = 1024
MAX_CONN = 10 # OPTIMIZE how many?

class TCPSocket:

    def __init__(self, sock=None):
        if sock:
            self.sock = sock
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data = b''

    def __getattr__(self, attr):
        return getattr(self.sock, attr)

class MonitorIO:
    def __init__(self, inputs):
        self.inputs = inputs
        readables, _, _ = select(inputs, [], [])
        self.readables = readables

class AsyncTCPEchoServ(TCPSocket):

    def __init__(self, port=PORT):

        super(AsyncTCPEchoServ, self).__init__()
        self.bind(('localhost', port))
        self.setblocking(0)
        print('Server listening on port', port)
        self.listen(MAX_CONN)
        inputs = [self.sock]

        while True:
            self.monitor_io = MonitorIO(inputs)
  
            for sock in self.monitor_io.readables:

               if sock is self.sock: # server?
                   new_conn, address = self.accept()
                   new_conn = TCPSocket(new_conn)
                   new_conn.setblocking(0)
                   self.monitor_io.inputs.append(new_conn)
                   current_peername = new_conn.getpeername()
                   print('Connected to:', current_peername)

               else: # client sent some data, process it
                   try: # Windows: when TCP program closes abruptly, exception

                       data = sock.recv(RECV_BUFFER)
                       if data:
                           AsyncTCPEchoServ.__data_transfer(sock, data)
                       else:
                           self.__handle_offline_client(sock, current_peername)

                   except socket.error as e:
                       sock.close()
                       self.__handle_offline_client(sock, current_peername)

    def __data_transfer(sock, data):

        print(len(data), 'bytes were received from:', sock.getpeername())
        data = sock.data + data

        if b'\n' in data:
            [data_send, data_delayed] = data.rsplit(b'\n', 1)
            sock.sendall(data_send + b'\n')
            sock.data += data_delayed
        else:
            sock.data += data

    def __handle_offline_client(self, sock, peername):
        print('Sock', peername, 'was closed by peer.')
        self.monitor_io.inputs.remove(sock)

if __name__ == '__main__':
    AsyncTCPEchoServ()