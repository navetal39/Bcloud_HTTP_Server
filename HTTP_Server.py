# INFO: #
# ===================================

print 'http'

'''
TO DO:
1) Find how to add the last update to last update page, then implement it.
2) Add TLS?
    
'''



# Imports: #
import re, urlparse, socket, Queue
from threading import Thread
from Utility import *
# from RECURRING_FUNCTIONS import secure_accept, secure_recv, secure_send, secure_close



# Constants: #
## General: ##
NUM_OF_THREADS = 20
SIZE_OF_QUEUE = 40

## Other usefull stuff: ##
STATUS_LINES = {"200": "HTTP/1.1 200 OK\r\n", "404": "HTTP/1.1 404 Not Found\r\n", "301": "HTTP/1.1 301 Moved Permanently\r\n",
                "302":"HTTP/1.1 302 Found\r\n", "500": "HTTP/1.1 500 Internal Server Error", "405": "HTTP/1.1 405 Method Not Allowed"}
MOVED = {"":"Pages/index.htm", "index.htm":"Pages/index.htm", "favicon.ico":"Pages/favicon.ico"}




# Methods: #
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

def get_length_from_pre_req(req):
    header_lines_list = req.split('\r\n')
    status_line = header_lines_list[0]; header_lines_list.remove(status_line)
    print status_line
    headers_list = header_lines_list
    for h in headers_list:
        print h
        name, cont = h.split(': ')
        if name.upper() == "Content-length".upper():
            return int(cont)

def send_status(path, read_type, status, sock, last_update=None, username=None):
    if status == "301":
        extra_header = "Location: {loc}\r\n".format(loc=MOVED[path])
        data = ""
    elif last_update:
        extra_header = ""
        data = open(path, read_type).read().format(UN=username, LUD=last_update)
    else:
        extra_header = ""
        data = open(path, read_type).read()
    headers = "Content-Length: {ln}\r\n{xh}".format(ln=len(data), xh=extra_header)
    status_line = STATUS_LINES[status]
    sock.send(status_line+headers+"\r\n"+data)
    

## General Methods: ##
def do_work():
    client_socket, client_addr = q.get()
    read_type = "r"
    folder_flag = False
    client_flag = False
    name = ""
    thread_server = get_server_for_thread() # It is an object representing a *client* of the main server.
    
    while True:
        req = client_socket.recv(2048)
        print 'got initial request'
        # Receive everything mechanism:
        while True:
            cont_len = get_length_from_pre_req(req)
            print cont_len
            if cont_len == None: #That means this header havn't been gotten yet.
                req+= client_socket.recv(2048)
                print 'got more stuff'
            else:
                print 'got len'
                while (len(req) < cont_len):
                    req += client_socket.recv(cont_len-len(req))
                    print 'got rest of stuff'
                break
            
        if req == "":
            client_socket.close()
            print "Closed connection" # -For The Record-
            q.task_done()
            break
        else:
            try:
                req_type = decide_type(req)
                parsed_request = parse_req(req)
                if req_type == "GET":
                    print "have a 'GET' request:\n", req
                    url = parsed_request[0]['url']
                    print "url: ", url
                    parsed_url = urlparse.urlparse(url)
                    print "parsed"
                    path = parsed_url.path.lstrip('/')
                    print path
                    params = parsed_url.query
                    print "param: ", params
                    if params: # Download or registery
                        print "params if"
                        status, path, folder_flag, name, last_update = download_or_register(thread_server, params)
                    else: # Normal 'GET'
                        print "normal GET"
                        if path == "favicon.ico":
                            path = "Pages/favicon.ico"
                            read_type = "rb"
                        elif path == "Files/client.zip":
                            print "client if"
                            client_zip = open("Files/client.zip", 'rb')
                            print "opened zip"
                            client_cont = client_zip.read()
                            print "read cont"
                            cont_len = len(client_cont)
                            client_socket.send(str(cont_len))
                            print "sent len"
                            resp = client_socket.recv(3)
                            print "recved"
                            if resp == 'ACK':
                                client_socket.send(client_cont)
                            else:
                                raise # Shouldn't get here at all...
                            client_flag = True
                        if path_exists(path):
                            status = "200"
                        elif path in MOVED.keys():
                            status = "301"
                        else:
                            status = "404"
                            path = ERROR_404_PATH

                elif req_type == "POST": # 405 Method Not Allowed
                    status = "405"
                    path = ERROR_405_PATH
                    #status, path = register(thread_server, parsed_request)
                
            except Exception, e: # That's an Internal Server Error (500)
                print "Error", e
                status = "500"
                path = ERROR_500_PATH

            finally:
                if folder_flag:
                    cont = get_folder(thread_server, name)
                    if cont == "WTF":
                        send_status(ERROR_404_PATH, read_type, "404", client_socket)
                    else:
                        client_socket.send('HTTP/1.1 200 OK\r\nContent-Length: {ln}\r\n\r\n{con}'.format(ln=len(cont), con=cont))
                        
                elif client_flag:
                    pass
                    
                else:
                    send_status(path, read_type, status, client_socket, last_update, name)
        
        
def make_threads_and_queue(num, size):
    global q
    q = Queue.Queue(size)
    for i in xrange(num):
        t = Thread(target=do_work)
        t.deamon = True
        t.start()


## Main Activity Method: ##
def run():
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
        client_socket, client_addr = server_socket.accept()
        print "A client accepted" # -For The Record-
        q.put((client_socket, client_addr))


'''
Exciting. Satisfying. Period.
.
'''
