SERVER_ADDRESS = "10.0.0.1"
SERVER_PORT = 4000

REQUESTER_ADDRESS = "10.0.0.2"
REQUESTER_PORT = 5000

FILE_NAME = "MOCK_DATA.csv"
BUFFER_SIZE = 1024 # 1024 bytes

# connected
# info:             print message
# file_size:        get file size from body
# sort_by:          field name to sort
# update: 
# delete:
# view:             print list of item
# file_received:    file transmitted
# error:            print error
# exit:

import sys, json

def toJson(dictionary_obj):
    dictionary_txt = str(dictionary_obj)

    return json.dumps(dictionary_obj)

def fromJson(json_text):
    return json.loads(json_text)

def padder(strng, padChar = "*", TARGETSIZE = 1024):
    curSize = sys.getsizeof(strng)

    if curSize <= TARGETSIZE:
        for i in range(0, 6):
            strng = padChar + strng 
        for i in range(TARGETSIZE - curSize - 6):
            strng = strng + padChar 

        return strng
    else:
        return strng
def unpadder(strng, padChar = "*"):
    return strng.replace(padChar, "")


def standardizeMsg(msg_obj, _TARGETSIZE = 1024):
    msg_txt = str(msg_obj.makeMsgJson())
    # return padder(msg_txt, padChar = "*", TARGETSIZE = _TARGETSIZE)
    return msg_txt

def unStandardizeMsg(msg_txt):
    return fromJson(unpadder(msg_txt))

class message:
    def __init__(self, msg_id = 0, msg_type = "info", msg_body = ""):
        self.d = {}
        self.d['id'] = msg_id
        self.d['type'] = msg_type
        self.d['body'] = msg_body
        
    def makeMsgJson(self):
        return toJson(self.d)

class item:
    def __init__(self, name, quantity, date):
        self.d = {}
        self.d['name'] = str(name)
        self.d['quantity'] = int(quantity)
        self.d['date'] = str(date)

    def makeItemJson(self):
        return toJson(self.d)

