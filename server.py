import socket, sys, os.path, csv, time, math, operator, datetime
import traceback
import logging

import env, protocol

HOST = env.SERVER_ADDRESS
PORT = int(env.SERVER_PORT)
BUFFER_SZ = env.BUFFER_SIZE
ID = 0

class Inventory_Managment:
    def __init__(self, baseDir):
        self.dblocation = baseDir + "/data/server/"
        self.dblocation = os.path.join(self.dblocation, env.FILE_NAME)

        if not os.path.exists(self.dblocation):
            open(self.dblocation, 'w+').close()

    def receiveInventoryFile(self, requester, number_pkt_file, sort_by = "name"):
        csv_data = []
        sorted_data = None
        
        with open(self.dblocation, 'wb') as file:
            for i in range(0, number_pkt_file):
                data = protocol.recv_msg(requester)

                if not data:
                    file.close()
                    break
                file.write(str(data))
        

        with open(self.dblocation, "r") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                csv_data.append(row)

        fields = csv_data.pop(0)
        
        if sort_by == "name":
            sorted_data = sorted(csv_data, key=operator.itemgetter(0))
            sorted_data.insert(0, fields)
        elif sort_by == "quantity":
            sorted_data = sorted(csv_data, key=operator.itemgetter(1))
            sorted_data.insert(0, fields)
        else:
            sorted_data = sorted(csv_data, key= lambda row: datetime.datetime.strptime(row[2], '%m/%d/%Y'))
            sorted_data.insert(0, fields)

        with open(self.dblocation,'w') as file:
            writer = csv.writer(file, dialect='excel')
            writer.writerows(sorted_data)
    
    def deleteItem(self, name):
        csv_data = []
        existed = False
        count = 0

        with open(self.dblocation, "r") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                csv_data.append(row)

        fields = csv_data.pop(0)

        for idx, val in enumerate(csv_data):
            if val[0].lower() == name.lower():
                csv_data.pop(idx)
                existed = True
                count = count + 1
        
        csv_data.insert(0, fields)
        with open(self.dblocation,'w') as file:
            writer = csv.writer(file, dialect='excel')
            writer.writerows(csv_data)

        if existed: return env.message(ID, "info", str(count) + " item(s) deleted").makeMsgJson()
        else: return env.message(ID, "info", "Item not found").makeMsgJson()

    def updateItem(self, item):
        item_obj = env.fromJson(item)
        
        standardizedObj = []
        standardizedObj.append(str(item_obj['name']))
        standardizedObj.append(str(item_obj['quantity']))
        standardizedObj.append(str(item_obj['date']))

        csv_data = []
        existed = False
        count = 0

        with open(self.dblocation, "r") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                csv_data.append(row)

        fields = csv_data.pop(0)

        for idx, val in enumerate(csv_data):
            if val[0].lower() == item_obj['name'].lower():
                csv_data[idx] = standardizedObj
                existed = True
                count = count + 1
        
        csv_data.insert(0, fields)
        with open(self.dblocation,'w') as file:
            writer = csv.writer(file, dialect='excel')
            writer.writerows(csv_data)

        if existed: return env.message(ID, "info", str(count) + " item(s) updated").makeMsgJson()
        else: return env.message(ID, "info", "Item not found").makeMsgJson()

    def viewItem(self, requester):
        csv_data = []
        
        with open(self.dblocation, "r") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                csv_data.append(row)

        fields = csv_data.pop(0)

        number_of_row = len(csv_data)
        protocol.send_msg(requester, env.message(ID, "info", str(number_of_row)).makeMsgJson().encode())
        
        for row in csv_data:
            protocol.send_msg(requester, str(row).encode())

def main():
    time.sleep(1) # wait to clear prev session pkt
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    
    server.bind((HOST, PORT))
    server.listen(2)

    while True:
        os.system('cls||clear')
        
        print("Server is listening at %s:%d." %(HOST, PORT))
        requester, req_address = server.accept()
        print("Connected with requester from", req_address)
        protocol.send_msg(requester, env.message(ID, "connected", "").makeMsgJson().encode())
        
        sort_by = "name"
        inv_man = Inventory_Managment(os.getcwd())

        while True:
            print("Waiting for requester's action...")
            
            msg_byte = protocol.recv_msg(requester)
            while not msg_byte:
                msg_byte = protocol.recv_msg(requester)
            msg_obj = env.fromJson(str(msg_byte))

            if msg_obj['type'] == 'exit': 
                print(" Session Ended\n")
                break
            
            elif msg_obj['type'] == 'sort_by':
                sort_by = msg_obj['body']

            elif msg_obj['type'] == 'file_size':
                print(" Downloading Inventory File")
                
                try:
                    number_pkt_file = (int(math.ceil((float(msg_obj['body']) / float(BUFFER_SZ)))))
                    inv_man.receiveInventoryFile(requester, number_pkt_file, sort_by)

                    protocol.send_msg(requester, env.message(ID, "file_received", "File Transmitted Successfully").makeMsgJson().encode())
                    
                    print(" Done")
                except Exception as e:
                    logging.error(traceback.format_exc())
                    protocol.send_msg(requester, env.message(ID, "error", "File Transmitted Failed").makeMsgJson().encode())
                    
            elif msg_obj['type'] == 'delete':
                print(" Deleting Item")
                try:
                    name = msg_obj['body']
                    msg_txt = inv_man.deleteItem(name)
                    
                    protocol.send_msg(requester, msg_txt.encode())

                    print(" Done")
                except Exception as e:
                    logging.error(traceback.format_exc())
                    protocol.send_msg(requester, env.message(ID, "error", "Server Failed").makeMsgJson().encode())
            
            elif msg_obj['type'] == 'update':
                print(" Updating Item")
                try:
                    item = msg_obj['body']
                    msg_txt = inv_man.updateItem(item)
                    
                    protocol.send_msg(requester, msg_txt.encode())

                    print(" Done")
                except Exception as e:
                    logging.error(traceback.format_exc())
                    protocol.send_msg(requester, env.message(ID, "error", "Server Failed").makeMsgJson().encode())

            elif msg_obj['type'] == 'view':
                print(" Sending Item View")
                try:
                    inv_man.viewItem(requester)

                    print(" Done")
                except Exception as e:
                    logging.error(traceback.format_exc())
                    protocol.send_msg(requester, env.message(ID, "error", "Server Failed").makeMsgJson().encode())

if __name__ == "__main__":
    main()

# requester.send("Thank you for connecting".encode())
# server.close()
# break