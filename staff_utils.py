import pickle
import pandas as pd
import socket
from config import *
import datetime

def staff_choice():
    print("0. View all patients")
    print("1. View Patient info")
    print("2. Admit Patient")
    print("3. Accept Payment")
    print("4. Charge Patient")
    print("5. Discharge Patient")
    print("6. Logout")
    choice = input("select one:")
    try:
        choice=int(choice)
        assert choice >=0 and choice <=6
        return choice
    except:
        print("invalid choice")
        staff_choice()



def view_all_patients(choice, is_valid):
    message = {}
    message["user_type"] = 3
    message["is_valid"] = is_valid
    message["choice"] = choice
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
    result = pd.DataFrame().from_dict(data=result, orient='index')
    result = result.fillna('N/A')
    print("List of all Patients:\n")
    print(result.to_string(index=False))
    print("-" * 20)
    print("Choose Again: ")


def view_patient_info(choice, is_valid):
    message = {}
    message["user_type"] = 3
    message["is_valid"] = is_valid
    message["choice"] = choice
    message["patient_id"]=int(input("enter patient id:"))
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
    #result = pd.DataFrame().from_dict(data=result, orient='index')
    print("Info about Patient:")
    print(print(result, 0))
    print("-" * 20)
    print("Choose Again: ")

def admit_patient(choice, is_valid):
    message = {}
    message["user_type"] = 3
    message["is_valid"] = is_valid
    message["choice"] = choice
    message["patient_name"]=str(input("enter patient's name: "))
    message["patient_age"]=int(input("enter patent's age in years: "))
    message["patient_room"]=int(input("enter bed number(101-199): "))
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
    if result["ack"]=="Successfully admitted":
        print(result["admitted_patient"])
    print("-" * 20)
    print("Choose Again: ")



def accept_payment(choice, is_valid):
    message = {}
    message["user_type"] = 3
    message["is_valid"] = is_valid
    message["choice"] = choice
    message["patient_id"] = int(input("enter patient's id: "))
    message["amount"]= float(input("enter amount to pay: "))
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
    if result["ack"] == "OK":
        print("payment successful")
        print("Receipt:\n{}".format(receipt.to_string(index=False)))
        print("\nAmount Due : {}".format(receipt["Amount"].sum()))

    print("-" * 20)
    print("Choose Again: ")




def charge_patient(choice, is_valid):
    message = {}
    message["user_type"] = 3
    message["is_valid"] = is_valid
    message["choice"] = choice
    message["patient_id"] = int(input("enter patient's id: "))
    message['charge_name'] = str(input("expense name(blood test, x-ray, etc.): "))
    message["charge_amount"] = float(input("enter amount to charge: "))
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
    if result["ack"] == "OK":
        print("successful")
        print("Receipt:\n{}".format(receipt.to_string(index=False)))
        print("\nAmount Due : {}".format(receipt["Amount"].sum()))

    print("-" * 20)
    print("Choose Again: ")


def discharge_patient(choice, is_valid):
    message = {}
    message["user_type"] = 3
    message["is_valid"] = is_valid
    message["choice"] = choice
    message["patient_id"] = int(input("enter patient's id: "))
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


def staff_activities(staff_name):
    print("Please choose one of the following")

    while True:
        choice = staff_choice()

        if choice==0:
            view_all_patients(choice=0, is_valid=True)

        elif choice==1:
            view_patient_info(choice=1, is_valid=True)

        elif choice == 2:
            admit_patient(choice=2, is_valid=True)

        elif choice == 3:
            accept_payment(choice=3, is_valid=True)

        elif choice==4:
            charge_patient(choice=4, is_valid=True)

        elif choice==5:
            discharge_patient(choice=5, is_valid=True)

        elif choice==6:
            print("Successfully logged out")
            break
        else:
            print("Invalid choice")

######### Server Side Functionality######

def staff_view_all_patients(server_patients_file):
    df = pd.read_csv(server_patients_file)
    return df.to_dict('index')


def staff_view_patient_info(server_patients_file, server_prescrib_file, patient_data):
    patient_id=int(patient_data["patient_id"])
    user_type=int(patient_data["user_type"])
    result={}
    df = pd.read_csv(server_patients_file)
    result["general_info"] = df[df["PatientID"] == patient_id].to_dict("index")
    if user_type==2 or user_type==4:
        df2=pd.read_csv(server_prescrib_file)
        result["med_history"] = df2[df2["PatientID"] == patient_id].to_dict("index")

    return result



def is_occupied(patients_file, bed_num):
    df = pd.read_csv(patients_file)
    res=list(zip(df["BedNum"].values, df["Status"].values))
    res=res[::-1]
    occupied=False
    for bed,status in res:
        if bed_num==bed and (status==0 or status==1):
            occupied=True
            break
    return occupied



def staff_admit_patient(server_patient_file, server_cost_file, patient_info):
    df = pd.read_csv(server_patient_file)
    patient_id=list(df["PatientID"])[-1]+1
    patient_name=patient_info["patient_name"]
    patient_age=patient_info["patient_age"]
    patient_adm_date = datetime.date.today()
    patient_room=int(patient_info["patient_room"])
    num_occupied_beds = len(df[df["Status"] != 2])
    result = {}
    if patient_room < 101 or patient_room >199:
        result["ack"] = "Invalid bed number. Only bed# 101 through 199 available"

    elif num_occupied_beds > 99:
        result["ack"] = "Sorry no bed available. All beds are occupied"

    elif is_occupied(server_patient_file, patient_room):
        result["ack"]="This bed is occupied. Choose another bed number."

    else:

        patient_status=0
        patient_discharge_date=""
        row=[patient_id, patient_name, patient_age,
             patient_adm_date, patient_room, patient_status, patient_discharge_date]
        patient_dict={k:v for (k,v) in zip(df.columns, row)}
        df = df.append(patient_dict, ignore_index=True)
        df.to_csv(server_patient_file, index=False)
        ###################################
        df = pd.read_csv(server_cost_file)
        row = [patient_adm_date,patient_id, "admission", 500.00]
        cost_dict={k:v for (k,v) in zip(df.columns, row)}
        df = df.append(cost_dict, ignore_index=True)
        df.to_csv(server_cost_file, index=False)
        ##################################

        result["ack"]="Successfully admitted"
        result["admitted_patient"]= patient_dict
    return result



def staff_accept_payment(server_cost_file, payment_info):
    df = pd.read_csv(server_cost_file)
    tr_date=datetime.date.today()
    patient_id=int(payment_info["patient_id"])
    tr_name="Payment"
    amount=float(payment_info["amount"])*-1.0
    row=[tr_date, patient_id, tr_name, amount]

    payment_dict={k:v for (k,v) in zip(df.columns, row)}
    df = df.append(payment_dict, ignore_index=True)
    df.to_csv(server_cost_file, index=False)
    #######################################
    result={}
    result["ack"]="OK"
    result["receipt"]=df[df["Patient_ID"]==patient_id].to_dict('index')
    return result



def staff_charge_patient(server_cost_file, charge_info):
    df = pd.read_csv(server_cost_file)
    tr_date=datetime.date.today()
    patient_id=int(charge_info["patient_id"])
    tr_name=str(charge_info["charge_name"])
    amount=float(charge_info["charge_amount"])
    row=[tr_date, patient_id, tr_name, amount]

    payment_dict={k:v for (k,v) in zip(df.columns, row)}
    df = df.append(payment_dict, ignore_index=True)
    df.to_csv(server_cost_file, index=False)
    #######################################
    result={}
    result["ack"]="OK"
    result["receipt"]=df[df["Patient_ID"]==patient_id].to_dict('index')
    return result


def staff_discharge_patient(server_patient_file, server_cost_file, patient_id):
    result={}
    df = pd.read_csv(server_patient_file)
    patient_status=df[df["PatientID"]==int(patient_id)]["Status"].values[0]

    df2=pd.read_csv(server_cost_file)
    amount_due=df2[df2["Patient_ID"]==int(patient_id)]["Amount"].sum()


    if patient_status != 1:
        result["ack"]="Need permission from doctor for discharge"

    elif amount_due != 0.0:
        result["ack"]="Amount Due: {}\n Clear Payment before discharge".format(amount_due)

    else:
        df.loc[df["PatientID"] == int(patient_id), "Status"] = 2
        df.loc[df["PatientID"] == int(patient_id), "DischargeDate"] = datetime.date.today()
        df.to_csv(server_patient_file, index=False)
        result["ack"]="Successfully Discharged patient: {}".format(patient_id)
    return result