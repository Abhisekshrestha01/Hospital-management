# coord.py
# Author: Nabin

import multiprocessing
import socket
from config import *
import pickle




def connect_to_server(server_ip, server_port, message):

    # create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to server
    sock.connect((server_ip, server_port))

    sock.sendall(bytes(message))

    msg_from_server = sock.recv(2048)
    #msg_from_server = pickle.loads(msg_from_server)
    sock.close()

    #print("Received result from Server {}: {}".format(server_ip, msg_from_server))
    return msg_from_server


def handle_message(connection, address, server1_connected, server2_connected):
    try:
        while True:
            data = connection.recv(2048)
            if len(data) == 0:
                break
            data = pickle.loads(data)
            print("Got following request from client({}):\n{}\n".format(address[0], data))

            if server1_connected.is_set() and server2_connected.is_set():
                print("Both servers({} and {}) are connected.\nSo, sending client request to both servers.".format(SERVER1_IP, SERVER2_IP))

                result_from_server1=connect_to_server(server_ip=SERVER1_IP, server_port=SERVER1_MSG_PORT,
                                                      message=pickle.dumps(data))

                result_from_server2=connect_to_server(server_ip=SERVER2_IP, server_port=SERVER2_MSG_PORT,
                                                      message=pickle.dumps(data))
                print("Got result back from both servers.")
                connection.send(bytes(result_from_server1))
                print("Result sent back to client({})\n".format(address[0]))

            elif server1_connected.is_set():
                print("Only Server1({}) is connected.So, sending client request to Server1 ".format(SERVER1_IP))
                result = connect_to_server(server_ip=SERVER1_IP, server_port=SERVER1_MSG_PORT,
                                           message=pickle.dumps(data))
                print("Got result back from Server1.")
                connection.send(bytes(result))
                print("Result sent back to client({})\n".format(address[0]))

            elif server2_connected.is_set():
                print("Only Server2({}) is connected.So, sending client request to Server2 ".format(SERVER2_IP))
                result = connect_to_server(server_ip=SERVER2_IP, server_port=SERVER2_MSG_PORT,
                                           message=pickle.dumps(data))
                print("Got result back from Server2.")
                connection.send(bytes(result))
                print("Result sent back to client({})\n".format(address[0]))

            else:
                #result={}
                #result["is_valid"]="server_down"
                #result=pickle.dumps(result, -1)
                #connection.send(bytes(result))
                print("Sorry! Both Servers are down.So, cannot process client request right now\n")

    except Exception as ex:
        print("EXCEPTION: {} ".format(ex))
        raise

    finally:
        #print("connection to {} closed".format(address))
        connection.close()




def handle_heartbeat(host, socket, hb_port, server_connected, server_joins, timeout_period, print_hb, server_id):
    socket.settimeout(timeout_period)
    socket.bind((host, hb_port))
    initial=True
    while True:
        try:
            data, address = socket.recvfrom(1024)
            if initial:
                print("Server{} connected.".format(server_id))
                server_connected.set()
                server_joins.set()
                initial=False
            data=data.decode('utf-8')
            if print_hb:
                print(data)
            server_joins.clear()

        except Exception as ex:
            if initial==False:
                print("Server{} is down.\n".format(server_id))
                server_connected.clear()
            initial=True

def handle_synchronization(server1_up, server2_up, server1_joins, server2_joins):
    while True:
        if server1_joins.is_set() and server2_up.is_set():
            print("Synchronizing Server1 to Server2.")
            # get data from server 2
            resync_msg = {}
            resync_msg["user_type"] = 0
            resync_msg["code"] = "get_data"

            result_from_server2 = connect_to_server(server_ip=SERVER2_IP,
                                                    server_port=SERVER2_MSG_PORT,
                                                    message=pickle.dumps(resync_msg))
            resync_msg = pickle.loads(result_from_server2)

            # write data to server 1
            resync_msg["code"] = "write_data"
            result_from_server1 = connect_to_server(server_ip=SERVER1_IP,
                                                    server_port=SERVER1_MSG_PORT,
                                                    message=pickle.dumps(resync_msg))

            result_from_server1 = pickle.loads(result_from_server1)

            if result_from_server1["ack"] == "OK":
                print("Server1 successfully synchronized to Server2.\n")


        elif server2_joins.is_set() and server1_up.is_set():
            print("Synchronizing Server2 to Server1.")
            # get data from server 1
            resync_msg = {}
            resync_msg["user_type"] = 0
            resync_msg["code"] = "get_data"

            result_from_server1 = connect_to_server(server_ip=SERVER1_IP,
                                                    server_port=SERVER1_MSG_PORT,
                                                    message=pickle.dumps(resync_msg))
            resync_msg = pickle.loads(result_from_server1)

            # write data to server 2
            resync_msg["code"] = "write_data"
            result_from_server2 = connect_to_server(server_ip=SERVER2_IP,
                                                    server_port=SERVER2_MSG_PORT,
                                                    message=pickle.dumps(resync_msg))

            result_from_server2 = pickle.loads(result_from_server2)

            if result_from_server2["ack"] == "OK":
                print("Server2 Successfully synchronized to Server1.\n")

        else:
            pass


class Coordinator(object):
    def __init__(self, hostname, msg_port, hb_port1,hb_port2, name="Coordinator"):
        self.hostname = hostname
        self.server1_connected=multiprocessing.Event()# True until server1 remains connected to coordinator
        self.server2_connected=multiprocessing.Event()# True until server2 remains connected to coordinator
        self.server1_joins=multiprocessing.Event()#True only when server1 joins coordinator
        self.server2_joins=multiprocessing.Event()#True only when server2 joins coordinator
        self.sync_done=multiprocessing.Event()#Flag to specify whether resyncing is complete
        self.msg_port = msg_port
        self.hb_port1 = hb_port1
        self.hb_port2 = hb_port2
        self.name = name
        self.print_heartbeat=False
        self.time_out_period=5
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket for client requests
        self.socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #socket for server1 heart beat monitoring
        self.socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #socket for server2 heart beat monitoring

    def monitor_heartbeat(self):
        hb1 = multiprocessing.Process(target=handle_heartbeat,
                                      args=(self.hostname, self.socket1, self.hb_port1,self.server1_connected,
                                            self.server1_joins, self.time_out_period, self.print_heartbeat, 1))
        hb2 = multiprocessing.Process(target=handle_heartbeat,
                                      args=(self.hostname, self.socket2, self.hb_port2,self.server2_connected,
                                            self.server2_joins,self.time_out_period, self.print_heartbeat, 2))
        hb1.daemon=True
        hb2.daemon=True
        hb1.start()
        hb2.start()

    def synchronize_servers(self):
        sync_process = multiprocessing.Process(target=handle_synchronization,
                                               args=(self.server1_connected, self.server2_connected,
                                                     self.server1_joins, self.server2_joins))
        sync_process.daemon=True
        sync_process.start()


    def start_service(self):
        print("{} Started\n".format(self.name))
        # TCP socket for handling message from client

        self.socket.bind((self.hostname, self.msg_port))
        self.socket.listen(5)
        while True:
            conn, address = self.socket.accept()
            #print("Got connection from {}".format(address))
            process = multiprocessing.Process(target=handle_message,
                                              args=(conn, address, self.server1_connected, self.server2_connected))
            process.daemon = True
            process.start()



if __name__=="__main__":

    coordinator = Coordinator(COORDINATOR_IP, COORDINATOR_MSG_PORT, COORDINATOR_HB_PORT1, COORDINATOR_HB_PORT2)
    try:
        coordinator.synchronize_servers()
        coordinator.monitor_heartbeat()
        coordinator.start_service()


    except Exception as ex:
        print("EXCEPTION: {} ".format(ex))
        raise

    finally:
        print("Shutting down")
        for process in multiprocessing.active_children():
            print("Shutting down process %r", process)
            process.terminate()
            process.join()
    print("done")