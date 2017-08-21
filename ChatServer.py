import socket, thread, pickle, logging, copy

logging.basicConfig(level=logging.DEBUG) #(filename='logefile.log', level=logging.INFO) switch to this to log to file

host = ''
port = 7878
max_connections = 5

userbase = {'JohnDoe':['password', 'Nickname']}
userbase_append_lock = thread.allocate_lock()

active_connections = []
active_connections_lock = thread.allocate_lock()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0) ##The key, turns off locks! Unsafe but useful with GIL

try:
    server.bind((host, port))
    logging.info('Successfully Bound to {}:{}'.format(host, port))
except socket.error as e:
    #print('Error binding: '+ str(e))
    logging.fatal('Error binding: '+ str(e))

server.listen(max_connections)

def ShowAll(msg, conns):
    for con in conns:
        #print (con)
        try:
            con.sendall(msg)
            logging.info('Msg sent')
        except Exception as e:
            logging.error('Failure to ShowAll, '+str(e))

def threaded_client(conn):
    ##Handle for these later, hash pass on server side btw
    conn.send(str.encode('!!Username: '))
    logged_in = False
    while logged_in == False:
        ##Login attempt loop
        username = ''
        while username == '' :
            try:
                username_en = conn.recv(2048)
                username = str(username_en.decode('utf-8'))
            except:
                pass
        conn.send(str.encode('!!Password'))
        password = ''
        while password == '' :
            try:
                password_en = conn.recv(2048)
                password = str(password_en.decode('utf-8'))
            except:
                pass
        if username not in userbase:
            ##Registration to do
            logging.info('User {} attempting to register'.format(username))
            conn.send(str.encode('Username {} does not exist, enter password to register'.format(username)))
        else:
            ##Pass check
            if userbase[username][0] == password:
                logging.info('User {} has logged in'.format(username))
                logged_in == True
                conn.send(str.encode('Login Sucessful \n'))
                if userbase[username][1] != '':
                    nickname = userbase[username][1]
                else:
                    nickname = username
                break
            else:
                logging.info('Incorrect password, user: {}'.format(username))
                conn.send(str.encode('Incorrect Password'))


    ##Sucessfully logged in, allow to send and receive now
    active_connections.append(conn)

    while True:
        others = copy.copy(active_connections)
        try:
            data = conn.recv(2048)
            d_data = str(data.decode('utf-8'))
            if not data:
                logging.INFO('User {} has quit'.format(username))
                break ##Exit server
            if d_data.startswith('!!'):
                ##command handling
                pass
            else:
                ##normal message
                #print(d_data)
                message = '{}: {}'.format(nickname, d_data)
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