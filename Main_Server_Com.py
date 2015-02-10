# INFO: #
# PreFirst version.
# No Encryption nor https (tls/ssl).
# ===================================

'''
To do:
1) Add "get folder" function.
'''

import socket


class Server(object):
    def __init__(self, ip, port):
        ''' This method will run every time you boot up the module.
        '''
        self.MAIN_IP = ip
        self.MAIN_PORT = port
        self.MAIN_SOCKET = socket.socket()
        self.send_list = []
        #self.MAIN_SOCKET.connect((MAIN_IP, MAIN_PORT))
    
    def __str__(self):
        return "ip: {ip}; port: {port}".format(ip=self.MAIN_IP, port=self.MAIN_PORT)
    
    def __repr__(self):
        return "################\nThe main server is (or at least should be) listening on:\nIP address: {ip}\nTCP port: {port}\n################".format(ip=self.MAIN_IP, port=self.MAIN_PORT)
    
    def create_user(self, name, pw):
        message = "REG;{n};{p}".format(n=name, p=pw)
        self.MAIN_SOCKET.send(message) #Encription? TLS?
        resp = self.MAIN_SOCKET.recv(1024)
        resp_parts = resp.split(';')
        flag = resp_parts[0]
        resp_parts.remove(flag)
        if resp_parts == message.split(';'):
            return "WTF" #Wat? :/
        else:
            return flag
        
    def get_last_update(self, folder_name):
        message = "LUD;{}".format(folder_name)
        self.MAIN_SOCKET.send(message)
        resp = self.MAIN_SOCKET.recv(1024)
        resp_parts = resp.split(';')
        flag = resp_parts[0]
        resp_parts.remove(flag)
        if resp_parts == message.split(';'):
            return "WTF"
        else:
            return flag, resp_parts[1]
        
    def get_folder(self, folder_name):
        pass

'''
Exciting. Satisfying. Period.
.
'''
