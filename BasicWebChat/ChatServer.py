import socket, thread, pickle, logging, copy

logging.basicConfig(level=logging.DEBUG) #(filename='logefile.log', level=logging.INFO) switch to this to log to file, maybe

host = ''
port = 7878
max_connections = 5

userbase = {'JohnDoe':['password', 'Nickname', False], 'Liv':['password1', 'Liv', False]}
userbase_append_lock = thread.allocate_lock()

active_connections = []
active_connections_lock = thread.allocate_lock()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0) ##The key, turns off locks! Unsafe but useful with GIL

bound = False
while bound == False:
    try:
        server.bind((host, port))
        logging.info('Successfully Bound to {}:{}'.format(host, port))
        bound = True
    except socket.error as e:
        #print('Error binding: '+ str(e))
        logging.error('Error binding: {}, attempting next port'.format(str(e)))
        port += 1

server.listen(max_connections)

def ShowAll(msg, conns):
    for con in conns:
        #print (con)
        try:
            con.sendall(msg)
            #print(msg)
            logging.debug('Msg sent')
        except Exception as e:
            logging.error('Failure to ShowAll, '+str(e))

def sanitize(strng):
    minus_breaks = strng.replace('\r\n', '')
    minus_newlines = minus_breaks.replace('\n', '')
    return minus_newlines

def threaded_client(conn):
    ##Handle for these later, hash pass on server side btw
    logged_in = False
    while logged_in == False:
        ##Login attempt loop
        conn.send(str.encode('!!Username: '))
        username = ''
        while username == '' :
            try:
                username_en = conn.recv(2048)
                username = str(username_en.decode('utf-8'))
                username = sanitize(username)
            except:
                pass
        conn.send(str.encode('!!Password: '))
        password = ''
        while password == '' :
            try:
                password_en = conn.recv(2048)
                password = str(password_en.decode('utf-8'))
                password = sanitize(password)
            except:
                pass
        if username not in userbase:
            ##Registration to do
            logging.info('User {} attempting to register'.format(repr(username)))
            conn.send(str.encode('Username {} does not exist, type !!yes to register a new account or anything else to try again: '.format(username)))
            register = ''
            while register == '':
                try:
                    #print ('start check')
                    register_en = conn.recv(2048)
                    register = str(register_en.decode('utf-8'))
                    register = sanitize(register)
                except:
                    pass
            if register == '!!yes':
                with userbase_append_lock:
                    userbase[username] = [password, username, True]
                logging.info('User {} has created an account'.format(username))
                conn.send(str.encode('Account sucessfully registered\n'))
                logged_in = True
                logging.info('New user {} has logged in'.format(username))
            else:
                ##Invalid, pass
                logging.info('User {} entered an invalid password'.format(username))
        else:
            ##Pass check
            if userbase[username][0] == password:
                logging.info('User {} has logged in'.format(username))
                logged_in == True
                conn.send(str.encode('Login Sucessful \n'))
                break
            else:
                logging.info('Incorrect password, user: {}'.format(username))
                conn.send(str.encode('Incorrect Password'))


    ##Sucessfully logged in, allow to send and receive now
    active_connections.append(conn)

    quitted = False
    while not quitted:
        others = copy.copy(active_connections)
        try:
            data = conn.recv(2048)
            d_data = str(data.decode('utf-8'))
            if not data:
                logging.INFO('User {} has quit'.format(username))
                break ##Exit server thread
            if d_data.startswith('!!'):
                ##command handling
                d_data = sanitize(d_data)
                d_data = d_data.lower()
                if d_data == '!!nick':
                    conn.send(str.encode('!!New Nickname: '))
                    newnick = ''
                    while newnick == '':
                        try:
                            newnick_en = conn.recv(2048)
                            newnick = str(newnick_en.decode('utf-8'))
                            newnick = sanitize(newnick)
                            with userbase_append_lock:
                                userbase[username][1] = newnick
                            logging.info('User {} set nickname to {}'.format(username, newnick))
                            others.remove(conn)
                            ShowAll(str.encode('User {} set nickname to {}\n'.format(username, newnick)), others)
                        except:
                            pass
                elif d_data == '!!quit':
                    #print('QUIT TEST')
                    logging.log('User {} disconnected'.format(username))
                    quitted = True
                    conn.shutdown(socket.SHUT_RDWR)
                    thread.exit()
                    break
            else:
                ##normal message
                #print(d_data)
                message = '{}: {}\n'.format(userbase[username][1], d_data)
                others.remove(conn)
                e_data = str.encode(message)
                ShowAll(e_data, others)
        except:
            pass



def main():
    try:
        conn, addr = server.accept()
        logging.info('Connected to {}:{}'.format(addr[0],addr[1]))
        thread.start_new(threaded_client, (conn,))
    except:
        pass

while True:
    main()