# INFO: #
# No Encryption (tls/ssl).
# ===================================


import socket, time
from RECURRING_FUNCTIONS import file_recv


class Server(object): # The HTTP server sees is as a server, the main server sees it as a client. Relativity! WOOHOO!
    ''' This class represents a client to the main server that the threads use as an interface to the main server.
    '''
    def __init__(self, ip, port):
        ''' This method will run every time you boot up the module.
        '''
        self.MAIN_IP = ip
        self.MAIN_PORT = port
        self.MAIN_SOCKET = socket.socket()
    
    def __str__(self):
		''' Used for debug.
		'''
        return "ip: {ip}; port: {port}".format(ip=self.MAIN_IP, port=self.MAIN_PORT)
    
    def __repr__(self):
		''' Used for debug.
		'''
        return "################\nThe main server is (or at least should be) listening on:\nIP address: {ip}\nTCP port: {port}\n################".format(ip=self.MAIN_IP, port=self.MAIN_PORT)

    def connect(self):
		''' Connects to the main server. Used for convenience.
		'''
        self.MAIN_SOCKET = socket.socket()
        self.MAIN_SOCKET.connect((self.MAIN_IP, self.MAIN_PORT))

    def disconnect(self):
		''' Disconnects (closes the socket) from the main server. Used for convenience.
		'''
        self.MAIN_SOCKET.close()
    
    def create_user(self, name, pw):
		''' This method asks the main server to register a new user. Then it return a flag implying whether it worked or not. 
		'''
        message = "REG|{n}|{p}".format(n=name, p=pw)
        self.connect()
        self.MAIN_SOCKET.send(message)
        resp = self.MAIN_SOCKET.recv(len(message) + 5)
        self.disconnect()
        resp_parts = resp.split('|')
        flag = resp_parts[0]; resp_parts.remove(flag)
        if resp_parts != message.split('|'): # The response is suposed to be a flag and then the request sent. If it's not - something is wrong (500).
            return "WTF"
        else:
            return flag
			
    def get_last_update(self, username, folder_type):
		''' Receives a username and a folder type (public/private) and returns the last time it was changed (or a flag implying if it was empty or does not exist).
		'''
		# Pass mission: #
        message = "LUD|{}|{}".format(username, folder_type)
        self.connect()
        self.MAIN_SOCKET.send(message)
        data = file_recv(self.MAIN_SOCKET)
        self.disconnect()
		# Check status: #
        if data == "EMPTY": # The folder that it's last update was requested is empty, so who gives.
            return "EMP", None
        elif data == "NNM": # There is no user, so no folder.
            return "NNM", None
        elif data == "WTF": # That's 500.
            raise
        else: # Process succeeded and 'data' is a list of '<file_name>:<last_update_in_seconds_since_1970>'.
			# Find the latest of the list so to know the last time the folder was updated: #
            data_list = data.split('\n')
            times = []
			## Assemble a list of times: ##
            for pair in data_list:
                try:
                    times.append(float(pair.split(':')[1]))
                except:
                    continue
            latest = max(times)
            return "SCS", time.asctime(time.localtime(latest))
        
    def get_folder(self, folder_name, count = 0):
        ''' Sends a request to get a specific folder. If it exists it should get a response
            in the flowing format: "SCS|<DATA>". If it does not it should get "NNM" and inform the HTTP server.
        '''
        self.connect()
        self.MAIN_SOCKET.send('GET|{}'.format(folder_name))
        final_response = file_recv(self.MAIN_SOCKET)
        self.disconnect()
        return final_response

'''
Exciting. Satisfying. Period.
.
'''
