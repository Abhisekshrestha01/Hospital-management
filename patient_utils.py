import pickle
import pandas as pd
import socket
from config import *
import datetime

def patient_choice():
    print("1. View Records")
    print("2. View Payments")
    print("3. Logout")
    choice = input("select one:")
    try:
        choice=int(choice)
        assert choice >=1 and choice <=3
        return choice
    except:
        print("invalid choice")
        patient_choice()




def view_records(choice, is_valid):
    message = {}
    message["user_type"] = 4
    message["is_valid"] = is_valid
    message["choice"] = choice
    message["patient_id"] = int(input("enter your patient id:"))
    message = pickle.dumps(message, -1)

    # create a TCP socket to connect to coordinator
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to coordinator
    sock.connect((COORDINATOR_IP, COORDINATOR_MSG_PORT))
    # send data to coordinator
    sock.sendall(bytes(message))

    # block till coordinator replies back
    result = sock.recv(2048)
    sock.close()
    result = pickle.loads(result)
    print("Patient Info:")
    print(result)
    print("-" * 20)
    print("Choose Again: ")


def view_payments(choice, is_valid):
    message = {}
    message["user_type"] = 4
    message["is_valid"] = is_valid
    message["choice"] = choice
    message["patient_id"] = int(input("enter your patient id:"))
    message = pickle.dumps(message, -1)

    # create a TCP socket to connect to coordinator
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to coordinator
    sock.connect((COORDINATOR_IP, COORDINATOR_MSG_PORT))
    # send data to coordinator
    sock.sendall(bytes(message))

    # block till coordinator replies back
    result = sock.recv(2048)
    sock.close()
    result = pickle.loads(result)
    receipt = pd.DataFrame().from_dict(data=result['receipt'], orient='index')
    print("Receipt:\n{}".format(receipt.to_string(index=False)))
    print("\nAmount Due : {}".format(receipt["Amount"].sum()))
    print("-" * 20)
    print("Choose Again: ")


def patient_activities(patient_name):
    print("Please choose one of the following")

    while True:
        choice = patient_choice()

        if choice==1:
            view_records(choice=1, is_valid=True)

        elif choice==2:
            view_payments(choice=2, is_valid=True)

        elif choice==3:
            print("Successfully logged out")
            break
        else:
            print("Invalid choice")

######### Server Side Functionality######

def patient_view_payments(server_cost_file, patient_id):
    df=pd.read_csv(server_cost_file)
    result={}
    result["receipt"]=df[df["Patient_ID"]==int(patient_id)].to_dict('index')
    return result
