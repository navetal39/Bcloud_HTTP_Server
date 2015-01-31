# INFO: #
# PreFirst version.
# No Encryption nor https (tls/ssl).
# ===================================


# Imports: #
import re, urlparse, socket, Queue
from threading import Thread



# Constants: #
NUM_OF_THREADS = 20
SIZE_OF_QUEUE = 40
MOVED = {'/':'Pages/index.htm'}
ERROR_404_PATH="Pages/Error404.html"
STATUS_LINES={"200": "HTTP/1.1 200 OK\r\n", "404": "HTTP/1.1 404 NOT FOUND\r\n", "301": "HTTP/1.1 301 Moved Permanently\r\n", "302":"HTTP/1.1 302 Found\r\n" }


# Methods: #
## SSL/TLS Methods: ##
def secure_accept(server_socket):
    ''' This method needs to accept a new client and establish a secure TCP connection with him (over SSL/TLS).
        It will return exacly what the normal accept method returns UNLESS we will need to change it.
    '''
    pass

def secure_recv(sock):
    ''' This method needs to receive the encrypted message (the ciphertext), decrypt it and return the plaintext.
    '''
    pass

def secure_send(sock, mess):
    ''' This method needs to...
    '''
    pass

## Small Help Methods: ##
def decide_type(req):
    GET_request_pattern = "GET .* HTTP/1.1\r\n.*"
    POST_request_pattern = "POST .* HTTP/1.1\r\n.*"
    
    try:
        if re.match(GET_request_pattern, req):
            return "GET"
        elif re.match(POST_request_pattern, req):
            return "POST"
        else:
            raise
    except: # That's an Internal Server Error (500)
        return "500"

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
    pass

def send_page(path, client_socket, status):
    if status == "301":#Unfinished... You can try to finish it if you feel like it!
        extra_line="Location: {}".format(MOVED[path])
        data=""
    else:
        data=open(path, 'r').read()
    headers = ".:.\r\n"
    status_line=STATUS_LINES(status)
    secure_send(client_socket, status_line+headers+"\r\n"+data)
    

## General Methods: ##
def do_work():
    client_scoket, client_addr = q.get()
    req = secure_recv(cliect_socket)
    req_type = decide_type(req)
    parsed_request=parse_req(req)
    if req_type == "GET":
        url = parsed_request[0]['url']
        parsed_url=urlparse.urlparse(url)
        path=parsed_url.path
        if path_exists(path):
            status="200"
        else:
            if path in MOVED.keys:
                status="301"
            else:
                status="404"
                path=ERROR_404_PATH
        send_page(path, client_socket, status)

    elif req_type == "POST":
        pass

    else: # That means it is an Internal Server Error (500)
        pass
    
def make_threads_and_queue(num, size):
    global q
    q = Queue(size)
    for i in xrange(num):
        t = Thread(target=do_work)
        t.deamon = True
        t.start()

## Main Activity Method: ##
def main():
    make_threads_and_queue(NUM_OF_THREADS, SIZE_OF_QUEUE)
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0',80))
    server_socket.listen(10)

    while True:
        client_socket, client_addr = secure_accept(server_socket)
        q.put((client_socket, client_addr))
    
