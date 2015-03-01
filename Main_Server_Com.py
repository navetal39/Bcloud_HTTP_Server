# INFO: #
# No Encryption (tls/ssl).
# get_folder not tested yet.
# ===================================


import socket, time


class Server(object):
    def __init__(self, ip, port):
        ''' This method will run every time you boot up the module.
        '''
        self.MAIN_IP = ip
        self.MAIN_PORT = port
        self.MAIN_SOCKET = socket.socket()
        self.send_list = []
        self.MAIN_SOCKET.connect((MAIN_IP, MAIN_PORT))
    
    def __str__(self):
        return "ip: {ip}; port: {port}".format(ip=self.MAIN_IP, port=self.MAIN_PORT)
    
    def __repr__(self):
        return "################\nThe main server is (or at least should be) listening on:\nIP address: {ip}\nTCP port: {port}\n################".format(ip=self.MAIN_IP, port=self.MAIN_PORT)
    
    def create_user(self, name, pw):
        message = "REG;{n};{p}".format(n=name, p=pw)
        self.MAIN_SOCKET.send(message)
        resp = self.MAIN_SOCKET.recv(1024)
        resp_parts = resp.split(';')
        flag = resp_parts[0]
        resp_parts.remove(flag)
        if resp_parts != message.split(';'):
            return "WTF"
        else:
            return flag
        
    def get_last_update(self, folder_name):
        message = "LUD;{}".format(folder_name)
        self.MAIN_SOCKET.send(message)
        resp = self.MAIN_SOCKET.recv(1024)
        resp_parts = resp.split(';')
        flag = resp_parts[0]
        resp_parts.remove(flag)
        if resp_parts != message.split(';'):
            return "WTF", "WTF"
        else:
            data = resp_parts[2]
            data_list = data.split('\n')
            times = []
            for pair in data_list:
                try:
                    times.append(float(pair.split('@')[1]))
                except:
                    pass
            latest = max(times)
            return flag, time.asctime(time.localtime(latest))
        
    def get_folder(self, folder_name, count = 0):
        ''' Sends a request to get a specific folder. If it exists it should get a response
            in the folowing format: "SCS;<DATA>". If it does not it should get "NNM".
            In the case the folder does not exist this function should load the dedicated
            HTML file and send it instead.
        '''
        sock=self.MAIN_SOCKET
        sock.send('GET;{}'.format(folder_name))
        response=sock.recv(5000)
        flag, str_size = response.split(';')
        try:
            if flag != 'SIZ':
                raise
            size = int(str_size)
        except:
            if count < 3: #Just making sure that it won't attemt endlessly
                sock.send('NAK')
                final_response = self.get_folder(sock, folder_name, count+1)
            else:
                final_response = 'WTF'
            return final_response
        else:
            seure_send(sock, 'ACK')
            final_response = sock.recv(size)
            return final_response

'''
Exciting. Satisfying. Period.
.
'''
