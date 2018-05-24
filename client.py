# client.py
# Author: Nabin
import socket
from config import *
import getpass
import pickle
from admin_utils import admin_activities
from staff_utils import staff_activities
from doctor_utils import doctor_activities
from patient_utils import patient_activities

def user_login():
    print("1.Admin\n2.Doctor\n3.Staff\n4.Patient")
    user_type = input("Login as: (choose 1 2 3 or 4): ")
    user_name = input("Username: ")
    password = getpass.getpass("Password: ")

    login_credentials = {
        "user_type": user_type,
        "user_name": user_name,
        "password": password,
        "is_valid": False
    }
    return login_credentials


def login_activity():

    # get login info from user
    login_credentials = user_login()

    #coordinator ip and port
    server_ip, server_port = COORDINATOR_IP, COORDINATOR_MSG_PORT

    # create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to server
    sock.connect((server_ip, server_port))

    # Loop until valid login
    while True:

        # send login details to coordinator
        login_credentials = pickle.dumps(login_credentials, -1)
        sock.sendall(bytes(login_credentials))

        # block till coordinator replies back
        result = sock.recv(1024)
        login_credentials = pickle.loads(result)


        # verify the validity of login
        if login_credentials["is_valid"]:
            print("successfully logged in ")
            break
        else:
            print("Invalid Credentials. Try again!")
            # repeat again if invalid login
            login_credentials = user_login()

    sock.close()
    return login_credentials




if __name__ == "__main__":

    print("WELCOME !!")

    login_credentials=login_activity()

    if login_credentials['user_type']=='1' and login_credentials["is_valid"]==True:
        admin_activities(login_credentials["user_name"])

    elif login_credentials['user_type']=='2' and login_credentials['is_valid']==True:
        doctor_activities(login_credentials["user_name"])

    elif login_credentials['user_type']=='3' and login_credentials['is_valid']==True:
        staff_activities(login_credentials["user_name"])

    elif login_credentials['user_type'] == '4' and login_credentials['is_valid'] == True:
        patient_activities(login_credentials["user_name"])
