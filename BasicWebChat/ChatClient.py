import socket, thread

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.setblocking(0) #Testing

print_lock = thread.allocate_lock()

def tx(conn, msg):
    en_msg = msg.encode()
    conn.send(en_msg)

def threaded_recv(conn):
    while True:
        data = conn.recv(2048)
        d_data = str(data.decode('utf-8'))
        print(d_data)
        if not data:
            print('ERROR: Host disconnected. Server shut down or lost connection.')
            quit()
            #break

def main():
    host = raw_input('Host: ')
    port = int(raw_input('Port: '))
    try:
        s.connect((host, port))
        print('Successfully connected to server')
        thread.start_new(threaded_recv, (s,))
    except socket.error as e:
        print(str(e))


    msg = ''
    while True:
        msg = str(raw_input(''))
        tx(s, msg)
        '''
        if msg.startswith('!!'):
            ##Command
            if msg.lower() == '!!quit':
                print('Quitting')
                s.close()
                break
            else:
                tx(s, msg)
                #print('sent command')

        else:
            ##Normal Message
            tx(s, msg)
            #print('sent')
        '''

main()
quit()