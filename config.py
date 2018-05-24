localhost="127.0.0.1"

sigma2="140.158.130.70"
sigma3="140.158.130.33"
sigma4="140.158.131.43"
sigma5="140.158.130.40"
sigma6="140.158.130.6"
sigma7="140.158.130.20"
sigma8="140.158.131.45"
sigma9="140.158.130.14"
sigma10="140.158.131.41"
sigma23="140.158.131.40"
sigma24="140.158.130.254"
sigma25="140.158.130.22"
sigma26="140.158.131.37"
sigma27="140.158.130.13"
sigma28="140.158.130.18"
sigma29="140.158.130.27"
sigma30="140.158.131.67"
##########################
SERVER1_USERS_FILE="users1.csv"
SERVER2_USERS_FILE="users2.csv"

SERVER1_PATIENTS_FILE="patients1.csv"
SERVER2_PATIENTS_FILE="patients2.csv"

SERVER1_COSTS_FILE="cost1.csv"
SERVER2_COSTS_FILE="cost2.csv"

SERVER1_PRESCRIB_FILE="prescrib1.csv"
SERVER2_PRESCRIB_FILE="prescrib2.csv"
##########################
import random

seed_value=101

random.seed(seed_value)
ports=random.sample(range(5000,8000), 10)

#COORDINATOR_IP = sigma4
COORDINATOR_IP = localhost
COORDINATOR_MSG_PORT = ports[0]
COORDINATOR_HB_PORT1 = ports[1]
COORDINATOR_HB_PORT2 = ports[2]

#SERVER1_IP = sigma7
SERVER1_IP = localhost
SERVER1_MSG_PORT = ports[3]
SERVER1_RESYNC_PORT=ports[4]


#SERVER2_IP = sigma8
SERVER2_IP = localhost
SERVER2_MSG_PORT = ports[5]
SERVER2_RESYNC_PORT = ports[6]
