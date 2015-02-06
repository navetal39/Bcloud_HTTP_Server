# INFO: #
# PreFirst version.
# No Encryption nor https (tls/ssl).
# ===================================



# Imports: #
import re, urlparse, socket, Queue
from threading import Thread
from os.path import isfile



# Constants: #
NUM_OF_THREADS = 20
SIZE_OF_QUEUE = 40
MOVED = {'':'Pages/index.htm', 'favicon.ico':'Pages/favicon.ico'}
ERROR_404_PATH = "Pages/Error404.htm"
ERROR_500_PATH = "Pages/Error500.htm"
STATUS_LINES = {"200": "HTTP/1.1 200 OK\r\n", "404": "HTTP/1.1 404 NOT FOUND\r\n", "301": "HTTP/1.1 301 Moved Permanently\r\n",
              "302":"HTTP/1.1 302 Found\r\n", "500": "HTTP/1.1 500 Internal Server Error"}
NO_NAME_ERROR_PATH = "Pages/ErrorNoName.htm"
EMPTY_FOLDER_ERROR_PATH = "Pages/ErrorEmptyFolder.htm"



# Methods: #
## SSL/TLS Methods: ##
def secure_accept(server_socket):
    ''' This method needs to accept a new client and establish a secure TCP connection with him (over SSL/TLS).
        It will return exacly what the normal accept method returns UNLESS we will need to change it.
    '''
    cs,ca = server_socket.accept()
    return (cs, ca)

def secure_recv(sock):
    ''' This method needs to receive the encrypted message (the ciphertext), decrypt it and return the plaintext.
    '''
    return sock.recv(5000) #Need to do the thing with the length...

def secure_send(sock, mess):
    ''' This method needs to get the message (the plaintext), encrypt it and send it (the ciphertext).
    '''
    print "sending {m}".format(m=mess) # -For The Record-
    sock.send(mess)

def secure_close(sock):
    ''' This method needs to...
    '''
    sock.close()


## Small Help Methods: ##
def decide_type(req):
    GET_request_pattern = "GET .* HTTP/1.1\r\n.*"
    POST_request_pattern = "POST .* HTTP/1.1\r\n.*"
    
    if re.match(GET_request_pattern, req):
        return "GET"
    elif re.match(POST_request_pattern, req):
        return "POST"
    else:  # That's an Internal Server Error (500)
        raise

def parse_req(req):
    ''' This method receives a http request and parse it.
        The methos returns the parsed message as follows:
        tuple with:
            1. A dictionary that contains the status line parsed as follows: {'method': <M>, 'url': <URL>, 'version': <V>}.
            2. A dictionary that contains the headers parsed as follows: {<header_name>:<header_value>,...}
            3. A string that contains the content of the message.
    '''
    header, content = req.split('\r\n\r\n')
    header_lines_list = header.split('\r\n')
    status_line = header_lines_list[0]
    header_lines_list.remove(status_line)
    headers_list = header_lines_list
    headers = dict()
    for h in headers_list:
        name, cont = h.split(': ')
        headers[name]=cont

    parts = status_line.split(' ')
    parsed_status_line = dict()
    parsed_status_line['method'] = parts[0]
    parsed_status_line['url'] = parts[1]
    parsed_status_line['version'] = parts[2]

    return (parsed_status_line, headers, content)

def path_exists(path):
    ''' For conventions, :P.
    '''
    return isfile(path)

def send_status(path, sock, status, read_type):
    if status == "301":
        extra_header = "Location: {loc}\r\n".format(loc=MOVED[path])
        data = ""
    else:
        extra_header = ""
        data = open(path, read_type).read()
    headers = "Content-Length: {ln}\r\n{xh}".format(ln=len(data),xh=extra_header)
    status_line = STATUS_LINES[status]
    secure_send(sock, status_line+headers+"\r\n"+data)
    

## General Methods: ##
def do_work():
    client_socket, client_addr = q.get()
    read_type = "r"
    req = secure_recv(client_socket)
    if req == "":
        secure_close(client_socket)
        print "Closed connection"
        q.task_done()
    else:
        try:
            req_type = decide_type(req)
            parsed_request = parse_req(req)
            if req_type == "GET":
                print "have a 'GET' request\n", req # -For The Record-
                url = parsed_request[0]['url']
                parsed_url = urlparse.urlparse(url)
                path = parsed_url.path.lstrip('/')
                params = parsed_url.query
                if params: # Download
                    key, value = params.split("=") # Because there is ONLY one parameter, for sure.
                    if key == "username": # Download first part.
                        if not name_exists(value):
                            path = NO_NAME_ERROR_PATH
                            status = "200"
                        if folder_empty(value):
                            path = EMPTY_FOLDER_ERROR_PATH
                            status = "200"
                        date = get_last_update(value)
                        path = LAST_UPDATE_FORM_PATH
                        
                    elif key == "is_approved": # Download second part.
                        pass
                
                else: # Normal 'GET'
                    if path == "favicon.ico":
                        path = "Pages/favicon.ico"
                        read_type = "rb"
                    if path_exists(path):
                        status = "200"
                    elif path in MOVED.keys():
                        status = "301"
                    else:
                        status = "404"
                        path = ERROR_404_PATH


            elif req_type == "POST": # Only registery
                form_content = parsed_request[2]
                params = get_params(form_content)
                form_type = decite_form_type(params)
                pass
            
        except: # That's an Internal Server Error (500)
            status = "500"
            path = ERROR_500_PATH
        finally:
            send_status(path, client_socket, status, read_type)
        
        
def make_threads_and_queue(num, size):
    global q
    q = Queue.Queue(size)
    for i in xrange(num):
        t = Thread(target=do_work)
        t.deamon = True
        t.start()


## Main Activity Method: ##
def main():
    port=80
    make_threads_and_queue(NUM_OF_THREADS, SIZE_OF_QUEUE)
    server_socket = socket.socket()
    while True:
        try:
            server_socket.bind(('0.0.0.0',port))
            break
        except:
            port+=1
    server_socket.listen(10)
    print "Running... on port {}".format(port) # -For The Record-

    while True:
        client_socket, client_addr = secure_accept(server_socket)
        print "A client accepted" # -For The Record-
        q.put((client_socket, client_addr))


main()

'''
Exciting. Satisfying. Period.
.
'''