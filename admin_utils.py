#utils.py
#Author: Nabin

import pandas as pd
import pickle
import socket
from config import *

roles={
    '1': "Admin",
    '2': "Doctor",
    '3': "Staff",
    '4': "Patient",
    1: "Admin",
    2: "Doctor",
    3: "Staff",
    4: "Patient"
}


############# Client side utility methods for administrator ###############

def admin_view_users(choice, is_valid):
    message = {}
    message["user_type"]=1
    message["is_valid"] = is_valid
    message["choice"] = choice
    message = pickle.dumps(message, -1)

    # create a TCP socket to connect to coordinator
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to coordinator
    sock.connect((COORDINATOR_IP, COORDINATOR_MSG_PORT))
    #send data to coordinator
    sock.sendall(bytes(message))

    # block till coordinator replies back
    result = sock.recv(2048)
    sock.close()
    result = pickle.loads(result)
    result = pd.DataFrame().from_dict(data=result, orient='index')
    print("Here is the list of all users:")
    print(result)
    print("-"*20)
    print("Choose Again: ")


def admin_add_new_user(choice,is_valid):
    message = {}
    message["user_type"] = 1
    message["is_valid"] = is_valid
    message["choice"] = choice
    print("Enter the details for the new user")
    message["new_user_type"]=input("enter user type(1-Admin, 2-Doctor,\n 3-Staff): ")
    message["new_user_name"]=input("enter user name :")
    message["new_user_pwd"]=input('enter password:')

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

    print("Successfully added follwing user")
    print("user name: {}".format(result["user_name"]))
    print("user type: {}".format(result["user_type"]))
    print("-" * 20)
    print("Choose Again: ")

def admin_delete_user(choice, is_valid):
    message={}
    message["user_type"] = 1
    message["is_valid"] = is_valid
    message["choice"] = choice
    print("Enter user type and user name to delete ")
    message["del_user_type"] = input("enter user type(1-Admin, 2-Doctor, 3-Staff): ")
    message["del_user_name"] = input("enter user name :")

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

    print("Successfully deleted follwing user")
    print("user name: {}".format(result["user_name"]))
    print("user type: {}".format(result["user_type"]))
    print("-" * 20)
    print("Choose Again: ")




def admin_choice():
    print("1. View all users")
    print("2. Add new user")
    print("3. Delete existing user")
    print("4. Logout")
    choice = input("select one:")
    try:
        choice=int(choice)
        assert choice >=1 and choice <=4
        return choice
    except:
        print("invalid choice")
        admin_choice()


def admin_activities(admin_name):
    print("Please choose one of the following".format(admin_name))

    while True:
        choice = admin_choice()

        if choice==1:
            admin_view_users(choice=1, is_valid=True)

        elif choice == 2:
            admin_add_new_user(choice=2, is_valid=True)

        elif choice == 3:
            admin_delete_user(choice=3, is_valid=True)

        elif choice==4:
            print("Successfully logged out")
            break
        else:
            print("Invalid Choice")


############# Server side utility methods for administrator ###############


def verify_login(user_type, user_name, password, server_users_file, server_patients_file):
    valid_user = False
    if str(user_type)=='4':#for patients username=name and password=patientid
        patients=pd.read_csv(server_patients_file).values
        for patient in patients:
            if str(patient[1]) == str(user_name) and \
                str(patient[0]) == str(password):
                valid_user=True
    else:#for other users
        users = pd.read_csv(server_users_file).values
        for user in users:
            if str(user[1]) == str(user_type) and \
                            str(user[2]) == str(user_name) and \
                            str(user[3]) == str(password):
                valid_user = True

    return valid_user


def show_user_details(server_users_file):
    df = pd.read_csv(server_users_file)
    return df[['user_id','user_name', 'role']].to_dict('index')



def add_user(server_users_file, user_type,
             user_name, password):
    df = pd.read_csv(server_users_file)
    user_id=list(df["user_id"])[-1]+1

    # add new entry
    df.loc[len(df)] = [user_id, user_type, user_name, password, roles[user_type]]
    df.to_csv(server_users_file, index=False)

    result={}
    result["user_type"]=roles[int(user_type)]
    result["user_name"]= user_name
    return result


def remove_user(server_users_file,
                user_type, user_name):
    df=pd.read_csv(server_users_file)
    new_df = df[~((df['user_type']==int(user_type)) & (df['user_name']==str(user_name)))]
    new_df.to_csv(server_users_file, index=False)
    result={}
    result["user_type"]=roles[user_type]
    result["user_name"]= user_name
    return result
