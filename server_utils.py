import multiprocessing
import socket
from config import *
import pickle
from admin_utils import verify_login, \
    remove_user, add_user, show_user_details

from staff_utils import staff_view_all_patients, \
    staff_view_patient_info, staff_admit_patient, \
    staff_accept_payment, staff_charge_patient, staff_discharge_patient

from doctor_utils import doctor_prescribe_medicine, \
    doctor_prescribe_test, doctor_approve_discharge

from patient_utils import patient_view_payments

import time



def get_data_from_file(filename):
    f=open(filename, "r")
    data=f.read()
    f.close()
    return data


def write_data_to_file(data, filename):
    f = open(filename, "w")
    f.write(data)
    f.close()
    return


def handle_message(connection, address, users_file, patients_file, cost_file, precrib_file):
    try:
        while True:
            data =connection.recv(2048)

            if len(data) == 0:
                break
            data = pickle.loads(data)
            #print("Data received from {} : {}".format(address, data))

            result = None

            #if it is a resync request
            if data["user_type"]==0 and "code" in data.keys():
                print("Request from Coordinator({}): synchronize".format(address[0]))
                result={}
                result["user_type"]=data["user_type"]
                #if it is a read request
                if data["code"]=="get_data":
                    result["users"]=get_data_from_file(filename=users_file)
                    result["cost"]=get_data_from_file(filename=cost_file)
                    result["patients"]=get_data_from_file(filename=patients_file)
                    result["prescrib"]=get_data_from_file(filename=precrib_file)
                    result["ack"]="OK"
                    result=pickle.dumps(result, -1)

                # if it is a write request
                elif data["code"]=="write_data":
                    users_data = data["users"]
                    cost_data = data["cost"]
                    patients_data=data["patients"]
                    prescrib_data=data["prescrib"]
                    write_data_to_file(data=users_data, filename=users_file)
                    write_data_to_file(data=cost_data, filename=cost_file)
                    write_data_to_file(data=patients_data, filename=patients_file)
                    write_data_to_file(data=prescrib_data, filename=precrib_file)
                    result["ack"] = "OK"
                    result = pickle.dumps(result, -1)

                # sending result back to coordinator
                connection.send(bytes(result))
                print("Synchronization successful\n")



            # if it is not a valid user check validity
            elif data["is_valid"]==False:
                print("Request from Coordinator({}): login".format(address[0]))
                data["is_valid"] = verify_login(data["user_type"], data["user_name"], data["password"], users_file, patients_file)
                result = pickle.dumps(data, -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")

            #if admin wants to see user details
            elif data["user_type"]==1 and data["choice"]==1:
                print("Request from Coordinator({}): show all users".format(address[0]))
                result = pickle.dumps(show_user_details(users_file), -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")


            #if admin wants to add new users
            elif data["user_type"]==1 and data["choice"]==2:
                print("Request from coordinator({}): add new user".format(address[0]))
                result=add_user(server_users_file=users_file,
                        user_type=data["new_user_type"],
                         user_name=data["new_user_name"],
                         password=data["new_user_pwd"])
                result=pickle.dumps(result, -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")

            #if admin wants to delete user
            elif data["user_type"]==1 and data["choice"]==3:
                print("Request from coordinator({}): delete existing user".format(address[0]))
                result=remove_user(server_users_file=users_file,
                                   user_type=data["del_user_type"],
                                   user_name=data["del_user_name"])
                result = pickle.dumps(result, -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")

            # if doctor wants to prescribe medicine
            elif data["user_type"] == 2 and data["choice"] == 2:
                print("Request from Coordinator({}): Prescribe Medicine".format(address[0]))
                result = pickle.dumps(doctor_prescribe_medicine(cost_file,precrib_file, data), -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")


            # if doctor wants to prescribe test
            elif data["user_type"] == 2 and data["choice"] == 3:
                print("Request from Coordinator({}): Prescribe Test".format(address[0]))
                result = pickle.dumps(doctor_prescribe_test(cost_file,precrib_file, data), -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")

            # if doctor wants to approve discharge
            elif data["user_type"] == 2 and data["choice"] == 4:
                print("Request from Coordinator({}): Approve Discharge".format(address[0]))
                result = pickle.dumps(doctor_approve_discharge(patients_file, data["patient_id"]), -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")


            #if staff wants to see all patients
            elif data["user_type"]==3 and data["choice"]==0:
                print("Request from Coordinator({}): show all patients".format(address[0]))
                result = pickle.dumps(staff_view_all_patients(patients_file), -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")


            #if staff or doctor or patient wants to see info about one patient
            elif (data["user_type"]==2 or data["user_type"]==3 or data["user_type"]==4) and data["choice"]==1:
                print("Request from Coordinator({}): View Patient info".format(address[0]))
                result = pickle.dumps(staff_view_patient_info(patients_file, precrib_file, data), -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")

            # if staff wants to admit a patient
            elif data["user_type"] == 3 and data["choice"] == 2:
                print("Request from Coordinator({}): Admit Patient".format(address[0]))
                result = pickle.dumps(staff_admit_patient(patients_file, cost_file, data), -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")


            # if staff wants to record payment
            elif data["user_type"] == 3 and data["choice"] == 3:
                print("Request from Coordinator({}): Save Payment".format(address[0]))
                result = pickle.dumps(staff_accept_payment(cost_file, data), -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")

            # if staff wants to charge patient
            elif data["user_type"] == 3 and data["choice"] == 4:
                print("Request from Coordinator({}): Charge Patient".format(address[0]))
                result = pickle.dumps(staff_charge_patient(cost_file, data), -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")

            # if staff wants to discharge patient
            elif data["user_type"] == 3 and data["choice"] == 5:
                print("Request from Coordinator({}): Discharge Patient".format(address[0]))
                result = pickle.dumps(staff_discharge_patient(patients_file, cost_file, data["patient_id"]), -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")

            #if patient wants to see payments
            elif data["user_type"] == 4 and data["choice"] == 2:
                print("Request from Coordinator({}): Payment info".format(address[0]))
                result = pickle.dumps(patient_view_payments(cost_file, data["patient_id"]), -1)
                connection.send(bytes(result))
                print("Result sent back to Coordinator\n")


    except Exception as ex:
        print("EXCEPTION: {} ".format(ex))
        raise

    finally:
        #print("connection to {} closed".format(address[0]))
        connection.close()

def handle_heartbeat(server_id, socket, hb_port, heartbeat_interval):
    try:
        hb_signal = "HB{}".format(server_id)
        hb_signal=bytes(hb_signal.encode('utf-8'))

        while True:
            socket.sendto(hb_signal, (COORDINATOR_IP, hb_port))
            time.sleep(heartbeat_interval)

    except Exception as ex:
        print("EXCEPTION: {} ".format(ex))
        raise

    finally:
        socket.close()



class Server(object):
    def __init__(self, hostname, msg_port, hb_port, server_id, users_file, patients_file, cost_file, prescrib_file):
        self.hostname = hostname
        self.msg_port = msg_port
        self.hb_port = hb_port
        self.server_id = server_id
        self.users_file = users_file
        self.patients_file = patients_file
        self.cost_file= cost_file
        self.prescrib_file=prescrib_file
        self.heartbeat_interval=3
        self.socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP socket for msg
        self.socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP socket for heartbeat

    def start_service(self):
        print("Server{} up and running \n".format(self.server_id))
        self.socket1.bind((self.hostname, self.msg_port))
        self.socket1.listen(5)

        while True:
            conn, address = self.socket1.accept()
            #print("Got connection from Coordinator {}".format(address[0]))
            process = multiprocessing.Process(target=handle_message, args=(conn, address,
                                                                           self.users_file,
                                                                           self.patients_file,
                                                                           self.cost_file,
                                                                           self.prescrib_file))
            process.daemon = True
            process.start()

    def send_heartbeat(self):
        hb_process = multiprocessing.Process(target=handle_heartbeat, args=(self.server_id, self.socket2,
                                                                            self.hb_port, self.heartbeat_interval))
        hb_process.daemon = True
        hb_process.start()


