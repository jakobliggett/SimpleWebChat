import socket, sys
from thread import *
#from dummy_thread import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setblocking(0)

host = ''
port = 11213

append_lock = allocate_lock()

error = True
while error:
    try:
        s.bind((host, port))
        error = False
    except socket.error as e:
        print(str(e))
        port +=1

print('Using port {}'.format(port))
s.listen(5) ##5 is max connections at once

def threaded_client(conn):
    conn.send(str.encode('Hello! \n'))

    while True:
        try:
            data = conn.recv(2048)
            dec_data = str(data.decode('utf-8'))
            print(dec_data)
            with append_lock:
                print(dec_data)
                with open('ChatData.txt', 'a') as f:
                    f.write(dec_data)
            reply = str('Server Output: '+dec_data)
            if not data:
                break
            conn.sendall(str.encode(reply))
        except:
            pass
    print('Con Broken')
    conn.close()

while True:
    try:
        connection, addr = s.accept()
        print(str(addr))
        start_new_thread(threaded_client, (connection,))
    except:
        pass