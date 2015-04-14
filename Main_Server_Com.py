# INFO: #
# No Encryption (tls/ssl).
# get_folder not tested yet.
# ===================================


import socket, time


class Server(object): # The HTTP server sees is as a server, the main server sees it as a client. Relativity! WOOHOO!
    def __init__(self, ip, port):
        ''' This method will run every time you boot up the module.
        '''
        self.MAIN_IP = ip
        self.MAIN_PORT = port
        self.MAIN_SOCKET = socket.socket()
    
    def __str__(self):
        return "ip: {ip}; port: {port}".format(ip=self.MAIN_IP, port=self.MAIN_PORT)
    
    def __repr__(self):
        return "################\nThe main server is (or at least should be) listening on:\nIP address: {ip}\nTCP port: {port}\n################".format(ip=self.MAIN_IP, port=self.MAIN_PORT)

    def connect(self):
        self.MAIN_SOCKET.connect((self.MAIN_IP, self.MAIN_PORT))

    def disconnect(self):
        self.MAIN_SOCKET.close()
    
    def create_user(self, name, pw):
        message = "REG|{n}|{p}".format(n=name, p=pw)
        self.connect()
        self.MAIN_SOCKET.send(message)
        resp = self.MAIN_SOCKET.recv(1024)
        self.disconnect()
        resp_parts = resp.split('|')
        flag = resp_parts[0]; resp_parts.remove(flag)
        if resp_parts != message.split('|'):
            return "WTF"
        else:
            return flag
        
    def get_last_update(self, username, folder_name):
        message = "LUD|{}|{}".format(username, folder_name)
        self.connect()
        self.MAIN_SOCKET.send(message)
        data = file_recv(self.MAIN_SOCKET)
        self.disconnect()
        data_list = data.split('\n')
        times = []
        for pair in data_list:
            try:
                times.append(float(pair.split(':')[1]))
            except:
                continue
        latest = max(times)
        return flag, time.asctime(time.localtime(latest))
        
    def get_folder(self, folder_name, count = 0):
        ''' Sends a request to get a specific folder. If it exists it should get a response
            in the folowing format: "SCS|<DATA>". If it does not it should get "NNM".
            In the case the folder does not exist this function should load the dedicated
            HTML file and send it instead.
        '''
        sock = self.MAIN_SOCKET
        self.connect()
        sock.send('GET|{}'.format(folder_name))
        response = sock.recv(2048) ################## Why not file_recv()? ########################
        flag, str_size = response.split('|')
        try:
            if flag != 'SIZ':
                raise
            size = int(str_size)
        except:
            if count < 3: #Just making sure that it won't attempt endlessly
                sock.send('NAK|'+response)
                final_response = self.get_folder(sock, folder_name, count+1)
            else:
                final_response = 'WTF'
        else:
            sock.send('ACK|'+response)
            final_response = sock.recv(size)
        finally:
            self.disconnect()
            return final_response

'''
Exciting. Satisfying. Period.
.
'''
