import struct

# Helper function to receice n bytes or return None if reach EOF
def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

# First 4c bytes ontains the message length
def send_msg(sock, msg):
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock):
    # Unpack and Read message length
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    
    msglen = struct.unpack('>I', raw_msglen)[0]
    
    # Read the message data
    return recvall(sock, msglen)

