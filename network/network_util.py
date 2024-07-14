import struct


# fixed: invalid load-key
# https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data

def __rec_val(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msg_len = __rec_val(sock, 4)
    if not raw_msg_len:
        return None
    # Read the message data
    return __rec_val(sock, struct.unpack('>I', raw_msg_len)[0])


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    sock.sendall(struct.pack('>I', len(msg)) + msg)
