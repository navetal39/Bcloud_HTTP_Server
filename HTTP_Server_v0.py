# INFO: #
# No Encryption nor https (tls/ssl).
# ===================================
'''
TO DO:
    1. Find how to add the last update to last update page, then implement it.
    2. Add TLS!
    
'''



# Imports: #
import re, urlparse, socket, Queue
from threading import Thread
from Utility import *



# Constants: #
## General: ##
NUM_OF_THREADS = 20
SIZE_OF_QUEUE = 40

## Other usefull stuff: ##
STATUS_LINES = {"200": "HTTP/1.1 200 OK\r\n", "404": "HTTP/1.1 404 Not Found\r\n", "301": "HTTP/1.1 301 Moved Permanently\r\n",
                "302":"HTTP/1.1 302 Found\r\n", "500": "HTTP/1.1 500 Internal Server Error"}
MOVED = {"":"Pages/index.htm", "favicon.ico":"Pages/favicon.ico"}




# Methods: #
## SSL/TLS Methods: ##
def secure_accept(server_socket):
    ''' This method needs to accept a new client and establish a secure TCP connection with him (over SSL/TLS).
        It will return exacly what the normal accept method returns UNLESS we will need to change it.
    '''
    cs,ca = server_socket.accept()
    return (cs, ca)

def secure_recv(sock, size = 5000):
    ''' This method needs to receive the encrypted message (the ciphertext), decrypt it and return the plaintext.
    '''
    return sock.recv(size)

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

def send_status(path, read_type, status, sock):
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
    folder_flag = False
    name = ""
    thread_server = get_server_for_thread()
    
    while True:
        req = secure_recv(client_socket)
        if req == "": # Qestions about download to Zeev; Tamir wrote, Tamir will understand! DON'T DELEAT!
            secure_close(client_socket)
            print "Closed connection" # -For The Record-
            q.task_done()
        else:
            try:
                req_type = decide_type(req)
                parsed_request = parse_req(req)
                if req_type == "GET":
                    print "have a 'GET' request:\n", req # -For The Record-
                    url = parsed_request[0]['url']
                    parsed_url = urlparse.urlparse(url)
                    path = parsed_url.path.lstrip('/')
                    params = parsed_url.query
                    if params: # Download 
                        status, path, folder_flag, name = download(thread_server, params, name)
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
                    status, path = register(thread_server, parsed_request)
                
            except: # That's an Internal Server Error (500)
                status = "500"
                path = ERROR_500_PATH

            finally:
                if folder_flag:
                    cont = get_folder(thread_server, name)
                    secure_send(client_socket, 'HTTP/1.1 200 OK\r\nContent-Length: {ln}\r\n\r\n{con}'.format(ln=len(cont), con=cont))
                else:
                    send_status(path, read_type, status, client_socket)
        
        
def make_threads_and_queue(num, size):
    global q
    q = Queue.Queue(size)
    for i in xrange(num):
        t = Thread(target=do_work)
        t.deamon = True
        t.start()


## Main Activity Method: ##
def main():
    port = 80
    make_threads_and_queue(NUM_OF_THREADS, SIZE_OF_QUEUE)
    server_socket = socket.socket()
    while True:
        try:
            server_socket.bind(('0.0.0.0', port))
            break
        except:
            port+=1
    server_socket.listen(6)
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
