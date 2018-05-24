# server2.py
# Author: Nabin
import multiprocessing
from server_utils import Server
from config import SERVER2_IP, SERVER2_MSG_PORT, \
    COORDINATOR_HB_PORT2, SERVER2_USERS_FILE, \
    SERVER2_PATIENTS_FILE, SERVER2_COSTS_FILE, SERVER2_PRESCRIB_FILE

if __name__ == "__main__":

    server2 = Server(hostname=SERVER2_IP,
                     msg_port=SERVER2_MSG_PORT,
                     hb_port=COORDINATOR_HB_PORT2,
                     server_id=2,
                     users_file=SERVER2_USERS_FILE,
                     patients_file=SERVER2_PATIENTS_FILE,
                     cost_file=SERVER2_COSTS_FILE,
                     prescrib_file=SERVER2_PRESCRIB_FILE)
    try:
        server2.send_heartbeat()
        server2.start_service()

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
