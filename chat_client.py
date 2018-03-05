"""
Python chat client
"""
import socket, sys, signal
if sys.version_info[0] < 3:
    import thread
#    sys.stderr.write("FATAL ERROR, CANNOT PROCEED\nPYTHON VERSION IS BELOW 3")
#    quit()
else:
    import _thread as thread

##CONFIGURABLES
BUFFER_SIZE = 2048

COLOR_RED   = "\033[1;31m"
COLOR_BOLD    = "\033[;1m"
COLOR_BLUE  = "\033[1;34m"
COLOR_GREEN = "\033[0;32m"
COLOR_RESET = "\033[0;0m"
##END CONFIGURABLES

print_lock = thread.allocate_lock()

def message_listening_handler(connection):
    while True:
        try:
            data = connection.recv(BUFFER_SIZE)
            if data:
                data_decoded = data.decode("utf-8")
                with print_lock:
                    if not data_decoded.startswith("!! "): ##Check if data or server command
                        print(data_decoded)
                    else:
                        command = data_decoded[3:]
                        print("COMMAND " + command)
            else:
                break ##If server disconnects, break read loop and handle the disconnect
        except: ##Error is thrown when there is no data, so we ignore it
            pass
    print("Lost connection to server!")
    close_connection(0, 0) ##Zeros are dummy data to act as signal


def close_connection(signal, frame): ##Use signal handler to implement
    print(COLOR_RESET+"\nQuitting...")
    try:
        listner.shutdown(socket.SHUT_RDWR)
    except:
        pass
    quit()

def main():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False

    while not connected:
        try:
            ip, port = (input("Enter 'ip:port' ~ ")).split(":")
            port = int(port)
            listener.connect((ip, port))
            print("Connected on {}:{}".format(ip, port))
            connected = True
        except Exception as e:
            print("Error connecting! \n{}".format(e))

    print("Use command+C to quit")
    ##User connected at this point, beginning to wait for messages to send
    thread.start_new(message_listening_handler, (listener,))
    while True:
        raw_data = input()
        data = str.encode(raw_data)
        listener.send(data)
    listener.close()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, close_connection)
    main()
