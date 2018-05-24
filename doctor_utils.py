import pickle
import pandas as pd
import socket
from config import *
import datetime

def doctor_choice():
    print("1. View Patient info")
    print("2. Prescribe Medicine")
    print("3. Prescribe Test")
    print("4. Approve Discharge")
    print("5. Logout")
    choice = input("select one:")
    try:
        choice=int(choice)
        assert choice >=1 and choice <= 5
        return choice
    except:
        print("invalid choice")
        doctor_choice()



def view_patient_info(choice, is_valid):
    message = {}
    message["user_type"] = 2
    message["is_valid"] = is_valid
    message["choice"] = choice
    message["patient_id"] = int(input("enter patient id:"))
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
    print("Info about Patient:")
    print(result)
    print("-" * 20)
    print("Choose Again: ")

def prescribe_medicine(choice, is_valid):
    message = {}
    message["user_type"] = 2
    message["is_valid"] = is_valid
    message["choice"] = choice
    message["patient_id"] = int(input("enter patient id: "))
    message["medicine"] = str(input("medicine name :"))
    message["price"]=float(input("Price($): "))
    message["comment"]=str(input("Comment: "))
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
    print(result["ack"])
    print("-" * 20)
    print("Choose Again: ")


def prescribe_test(choice, is_valid):
    message = {}
    message["user_type"] = 2
    message["is_valid"] = is_valid
    message["choice"] = choice
    message["patient_id"] = int(input("enter patient id: "))
    message["test"] = int(input("Tests Available:\n1.blood, 2.urine, 3.x-ray, 4.ecg\nchoose(1/2/3/4): "))
    message["comment"] = str(input("Comment: "))
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
    print(result["ack"])
    print("-" * 20)
    print("Choose Again: ")

def approve_discharge(choice, is_valid):
    message = {}
    message["user_type"] = 2
    message["is_valid"] = is_valid
    message["choice"] = choice
    message["patient_id"] = int(input("enter patient id:"))
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
    print(result["ack"])
    print("-" * 20)
    print("Choose Again: ")


def doctor_activities(doctor_name):
    print("Please choose one of the following")

    while True:
        choice = doctor_choice()

        if choice == 1:
            view_patient_info(choice=1, is_valid=True)

        elif choice == 2:
            prescribe_medicine(choice=2, is_valid=True)

        elif choice == 3:
            prescribe_test(choice=3, is_valid=True)

        elif choice == 4:
            approve_discharge(choice=4, is_valid=True)

        elif choice == 5:
            print("Successfully logged out")
            break
        else:
            print("Invalid choice")


######################################
#Server Side Functionalities
######################################

def doctor_prescribe_medicine(server_cost_file, server_prescrib_file, message):
    tr_date = datetime.date.today()
    patient_id=int(message["patient_id"])
    medicine=str(message["medicine"])
    comment=str(message["comment"])
    price = float(message["price"])

    #update prescrib file
    df = pd.read_csv(server_prescrib_file)
    row=[tr_date, patient_id, medicine, comment]
    prescrib_dict={k:v for (k,v) in zip(df.columns, row)}
    df = df.append(prescrib_dict, ignore_index=True)
    df.to_csv(server_prescrib_file, index=False)

    #update cost file
    df = pd.read_csv(server_cost_file)
    row=[tr_date,patient_id,medicine, price]
    cost_dict = {k: v for (k, v) in zip(df.columns, row)}
    df = df.append(cost_dict, ignore_index=True)
    df.to_csv(server_cost_file, index=False)

    result={}
    result['ack']="Done"
    return result


def doctor_prescribe_test(server_cost_file, server_prescrib_file, message):
    tr_date = datetime.date.today()
    patient_id=int(message["patient_id"])
    test=int(message["test"])
    comment=str(message["comment"])
    test_names={1:"blood test",
            2:"urine test",
            3:"x ray",
            4:"ecg"}
    medicine=test_names[test]
    test_prices={1:100.0,
            2:200.0,
            3:300.0,
            4:400.0}
    price=test_prices[test]

    #update prescrib file
    df = pd.read_csv(server_prescrib_file)
    row=[tr_date, patient_id, medicine, comment]
    prescrib_dict={k:v for (k,v) in zip(df.columns, row)}
    df = df.append(prescrib_dict, ignore_index=True)
    df.to_csv(server_prescrib_file, index=False)

    #update cost file
    df = pd.read_csv(server_cost_file)
    row=[tr_date,patient_id,medicine, price]
    cost_dict = {k: v for (k, v) in zip(df.columns, row)}
    df = df.append(cost_dict, ignore_index=True)
    df.to_csv(server_cost_file, index=False)

    result={}
    result['ack']="Done"
    return result




def doctor_approve_discharge(server_patient_file, patient_id):
    df = pd.read_csv(server_patient_file)
    df.loc[df["PatientID"] == int(patient_id), "Status"] = 1
    df.to_csv(server_patient_file, index=False)
    result={}
    result["ack"] = "Successfully approved Discharge for patient: {}".format(patient_id)
    return result
