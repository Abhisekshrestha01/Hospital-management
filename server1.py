# server1.py
# Author: Nabin
import multiprocessing
from server_utils import Server
from config import SERVER1_IP, SERVER1_MSG_PORT, \
    COORDINATOR_HB_PORT1,SERVER1_USERS_FILE,\
    SERVER1_PATIENTS_FILE, SERVER1_COSTS_FILE, SERVER1_PRESCRIB_FILE


if __name__ == "__main__":

    server1 = Server(hostname=SERVER1_IP,
                     msg_port=SERVER1_MSG_PORT,
                     hb_port=COORDINATOR_HB_PORT1,
                     server_id=1,
                     users_file=SERVER1_USERS_FILE,
                     patients_file=SERVER1_PATIENTS_FILE,
                     cost_file=SERVER1_COSTS_FILE,
                     prescrib_file=SERVER1_PRESCRIB_FILE)

    try:
        server1.send_heartbeat()
        server1.start_service()

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
