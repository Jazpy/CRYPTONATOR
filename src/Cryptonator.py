#!/usr/bin/python3

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

    def eval(self):
        
        # Get current message
        msg = self.irc_sock.recv(2048).decode('UTF-8')
        msg = msg.strip('\n\r')
        print(msg)

        # Special case for server pings
        if 'PING :' in msg:
            return self.ping()

        # Else it's a PRIVMSG, extract name and text
        if 'PRIVMSG' not in msg:
            return 0

        sender = msg.split('!', 1)[0][1:].lower()
        text = msg.split('PRIVMSG',1)[1].split(':',1)[1]

        # Validate sender before replying
        if len(sender) > 16 or sender != self.admin:
            return 0
        
        # Choose what action to take
        if 'Hello' in text:
            return self.tell('World!')

        elif 'EXIT' in text:
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
