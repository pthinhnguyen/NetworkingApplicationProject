import socket, os, sys, csv, time, datetime
import traceback
import logging

import env, protocol

HOST = env.REQUESTER_ADDRESS
PORT = int(env.REQUESTER_PORT)
BUFFER_SZ = env.BUFFER_SIZE

ID = 0
clear = lambda: os.system('cls')

class Inventory_Requester:
    def __init__(self, baseDir):
        self.dblocation = baseDir + "/data/requester/"
        self.dblocation = os.path.join(self.dblocation, env.FILE_NAME)
    
    def sendInventoryFile(self, requester):
        file = open(self.dblocation, "rb")
        file_size = os.path.getsize(self.dblocation)
        
        protocol.send_msg(requester, env.message(msg_id=ID, msg_type= "file_size", msg_body= str(file_size)).makeMsgJson().encode())

        while True:
            pkt = file.read(BUFFER_SZ)
            while (pkt):
                protocol.send_msg(requester, pkt.encode())
                pkt = file.read(BUFFER_SZ)
            if not pkt:
                file.close()
                break
        
        msg_byte = protocol.recv_msg(requester)
        while not msg_byte:
            msg_byte = protocol.recv_msg(requester)
        msg_obj = env.fromJson(str(msg_byte))
        
        return msg_obj

def menu_main():
    action = -1
    
    opt_main = [
        "[0] Upload Inventory File", 
        "[1] Delete item",
        "[2] Update item",
        "",
        "[3] Exit"
    ]

    print("---Welcome to Inventory Management---")
    
    for opt in opt_main:
        print("   " + opt)
    
    while True:
        try:
            _action = raw_input("Your Action:   ")
            action = int(_action)
            if (action >= 0 and action <=3): return action
            else: raise ValueError("Invalid Input")
        except Exception as e:    
            pass

def menu_sub(sub_code):
    action = -1
    
    opt_0_sort = [
        "[0] by Name",
        "[1] by Quantiy",
        "[2] by Inventory Date"
    ]

    if (sub_code == 0):
        sorted_by = "name"
        
        print("Sort Inventory File By")
        for opt in opt_0_sort:
            print("   " + opt)
        
        while True:
            try:
                _action = raw_input("Your Action:   ")
                action = int(_action)
                if (action == 0): 
                    sorted_by = "name"
                    break
                elif (action == 1): 
                    sorted_by = "quantity"
                    break
                elif (action == 2): 
                    sorted_by = "date"
                    break
                else: raise ValueError("Invalid Input")
            except Exception as e:    
                pass
        return sorted_by
    
    elif(sub_code == 1):
        print("Delete Item By Name\n")
        name = raw_input("Item Name:  ")
        return name

    elif(sub_code == 2):
        print("Update Item By Name\n")
        print("\nNew Value")
        
        while True:
            name = raw_input("Name:  ")
            
            quantity = 0
            while True:    
                try:
                    quantity = int(raw_input("Quantity:  "))
                    break
                except Exception as e:    
                    pass
            
            inv_date = str(datetime.datetime.now().strftime('%m/%d/%Y'))
            print("Inventory Date:  %s\n" % inv_date)

            isConfirm = raw_input("Confirm? (yes/y or no/n)  ")
            if (isConfirm.lower() == "yes" or isConfirm.lower() == "y"): 
                return env.item(name, quantity, inv_date).makeItemJson()
            else: print("")
        
def main():
    requester = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    requester.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    requester.bind((HOST, PORT))
    requester.connect((env.SERVER_ADDRESS, env.SERVER_PORT))

    connection_result = env.fromJson(str(protocol.recv_msg(requester)))

    if (connection_result['type'] != 'connected'):  # connection failed
        return

    while True:
        os.system('cls||clear')
        action = menu_main()

        if (action == 0):
            os.system('cls||clear')
            
            # Sort by
            sort_by = menu_sub(0)
            protocol.send_msg(requester, env.message(msg_id=ID, msg_type= "sort_by", msg_body = sort_by).makeMsgJson().encode())

            # Send File
            inv_req  = Inventory_Requester(os.getcwd())
            result = inv_req.sendInventoryFile(requester)

            if result['type'] == 'file_received': 
                print(result['body'])
            elif result['type'] == 'error': 
                print(result['body'])
            
            raw_input("Press any key to continue...")
        elif (action == 1):
            os.system('cls||clear')
            name = menu_sub(1)

            protocol.send_msg(requester, env.message(msg_id=ID, msg_type= "delete", msg_body = name).makeMsgJson().encode())
            
            msg_byte = protocol.recv_msg(requester)
            while not msg_byte:
                msg_byte = protocol.recv_msg(requester)
            msg_obj = env.fromJson(str(msg_byte))
            
            print("\n" + msg_obj['body'])

            raw_input("Press any key to continue...")
        elif (action == 2):            
            os.system('cls||clear')
            item = menu_sub(2)
            
            protocol.send_msg(requester, env.message(msg_id=ID, msg_type= "update", msg_body = item).makeMsgJson().encode())

            msg_byte = protocol.recv_msg(requester)
            while not msg_byte:
                msg_byte = protocol.recv_msg(requester)
            msg_obj = env.fromJson(str(msg_byte))
            
            print("\n" + msg_obj['body'])

            raw_input("Press any key to continue...")  
        elif (action == 3):
            break
        else:
            pass
    protocol.send_msg(requester, env.message(msg_id=ID, msg_type= "exit", msg_body= "").makeMsgJson().encode())

    time.sleep(1)   # wait for server close connection
    requester.close()

if __name__ == "__main__":
    sys.exit(main())
