# INFO: #
# ===================================

print 'http'

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
                "302":"HTTP/1.1 302 Found\r\n", "500": "HTTP/1.1 500 Internal Server Error\r\n", "405": "HTTP/1.1 405 Method Not Allowed"} # Used to ease the process of finding the needed status line for that specific status code.
MOVED = {"":"Pages/index.htm", "index.htm":"Pages/index.htm", "favicon.ico":"Pages/favicon.ico"} # Pages that need to return a 301 Moved Permanently status line.

PICS_EXTENTIONS = ['.jpeg', '.jpg', '.png', '.gif', '.ico'] # Used later to identify pictures in order to add the speciel HTTP header needed.
PICS_TYPES = {'.jpeg': 'image/jpeg', '.jpg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif', '.ico': 'image/x-icon'} # Used to ease the process of finding the needed header for that specific image type.



# Methods: #
## Small Help Methods: ##
def decide_type(req):
    ''' Receives a HTTP req and returns a string implying which HTTP request type is it (POST/GET).
    '''
    # These two patterns uses regular expressions according to the library 're': 
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

def is_picture(path):
    ''' Receives a path and returns a boolean implying whether it is to a picture or not (uses PICS_EXTENTIONS).
    '''
    for ext in PICS_EXTENTIONS:
        if path.lower().endswith(ext):
            return True

def get_image_type(path):
    ''' Receives a path to a picture and returns the extra HTTP header it requires (uses PICS_EXTENTIONS and PICS_TYPES).
    '''
    pre_type = ""
    for ext in PICS_EXTENTIONS:
        if path.lower().endswith(ext):
            pre_type = ext
            break
    return PICS_TYPES[pre_type]

def send_status(path, status, sock, last_update=None, username=None):
    ''' This methods receives a path, an HTTP status code and a socket (plus two optional parameters that their purpose will be detailed ahead).
        The method sends the content of the file to the socket via an HTTP response with the status code received.
        The two optional parameters - last update and username - are used to determine whether it is a special case that is a part of the public folder download process.
    '''
    if status == "301":
        extra_header = "Location: {loc}\r\n".format(loc=MOVED[path])
        data = ""
    elif status == "404": # To solve a specific problem with the paths in the 404 page:
        status = "301"
        extra_header = "Location: {loc}\r\n".format(loc="/"+path)
        data = ""
    elif last_update and path == LAST_UPDATE_PLUS_PATH: # A part in the process of public folder download that requires special care:
        extra_header = ""
        print 'opening (in LU) ' + path
        data = open(path, 'r').read().format(UN=username, LUD=last_update) # Insert the username and tha last update to the HTML page.
        print "opened (in LU) " + path
    elif is_picture(path): # Pictures require spiecal extra header "Content-type":
        extra_header = "Content-type: {}\r\n".format(get_image_type(path))
        print 'opening (in rb) ' + path
        data = open(path, 'rb').read()
        print "opened (in rb) " + path
    else: # The defult case:
        extra_header = ""
        print 'opening (in normal) ' + path
        data = open(path, 'r').read()
        print "opened (in normal) " + path
    headers = "Content-Length: {ln}\r\n{xh}".format(ln=len(data), xh=extra_header) # Assemble the HTTP header.
    status_line = STATUS_LINES[status] # See the explanation of the STATUS_LINES in the top.
    sock.send(status_line+headers+"\r\n"+data) # Assemble and send the HTTP response.
    

## General Methods: ##
def do_work():
    ''' The method that the Thread does.
    '''
    while True:
        # Get task, intial things...:
        client_socket, client_addr = q.get() #New client to handle!
        thread_server = get_server_for_thread() # Getting the object that represents a *client* of the main server.
        
        while True:
            try:
                req = client_socket.recv(4096)
                print 'got request' # -For The Debug-
            except Exception, e: # If there is a problem receiving from the client - we close the connection:
                print 'ERROR',e # -For The Debug-
                print e.errno # -For The Debug-
                req = "" # Well actually, we change 'req' to contain nothing so it will be closed as all other connections are.
            folder_flag = False; client_flag = False; last_update = None # Flags, see use below (in the end of method).
            name = "" # So there won't be a "Referenced before assignment error"...
            
            if req == "": # When a client closes the connection - the server receives an empty string.
                client_socket.close()
                print "Closed connection" # -For The Record-
                q.task_done()
                break
            else:
                try:
                    # Determine request type: #
                    req_type = decide_type(req)
                    if req_type == "GET":
                        # Get ready to handle: #
                        print "have a 'GET' request:\n", req # -For The Record-
                        parsed_request = parse_req(req)
                        url = parsed_request[0]['url']
                        print "url: ", url # -For The Debug-
                        parsed_url = urlparse.urlparse(url)
                        print "parsed" # -For The Debug-
                        path = parsed_url.path.lstrip('/') # Delete the '/' from the beginning of the path.
                        print path # -For The Debug-
                        params = parsed_url.query # The url parameters
                        print "param: ", params # -For The Debug-
						
                        if params: # If there were url parameters - it means the user either asks for a public folder download or for registry.
                            print "params if" # -For The Debug-
                            status, path, folder_flag, name, last_update = download_or_register(thread_server, params)
							
                        else: # Normal 'GET'
                            print "normal GET"  # -For The Record-
                            # Specific cases: #
                            if path == "favicon.ico": # We deal with favicon specially - the path is needed to be changed
                                path = "Pages/favicon.ico"
                            elif path == "Files/client.zip": # That means the Bcloud_installer is requesting for the client program - it needs to be handled a little differently: We first send the length and only after it is approved to be received we send the file itself.
                                print "client if" # -For The Debug-
                                client_zip = open("Files/client.zip", 'rb');    print "opened zip" # -For The Debug-
                                client_cont = client_zip.read();    print "read cont" # -For The Debug-
                                cont_len = len(client_cont)
                                client_socket.send(str(cont_len)) # Sending the length first.
                                print "sent len" # -For The Debug-#
                                resp = client_socket.recv(3);   print "received" # -For The Debug-
                                if resp == 'ACK': # We got the approval,
                                    client_socket.send(client_cont) # So we send the file.
                                else: # If it got in here... God knows why...
                                    raise # And god will help this error.
                                client_flag = True # So it wont go in to 'send_status()' later.
							
                            # In general: #
                            if path_exists(path): # If we are in here - LG!
                                status = "200"
                            elif path in MOVED.keys():
                                status = "301"
                            else:
                                status = "404"
                                path = ERROR_404_PATH

                    elif req_type == "POST": # 405 Method Not Allowed
                        status = "405"
                        path = ERROR_405_PATH
                    
                except Exception, e: # 500 Internal Server Error
                    print "Error", e # -For The Debug-
                    status = "500"
                    path = ERROR_500_PATH

                finally:
                    if folder_flag: # That means we need to get the folder from the main server and send it (because it is phase 2):
                        cont = get_folder(thread_server, name)
                        if cont == "WTF": # Some error getting the user's folder:
                            send_status(ERROR_404_PATH, "404", client_socket)
                        else: # The browser will just download what he'll get (as it is defined in the HTML page):
                            client_socket.send('HTTP/1.1 200 OK\r\nContent-Length: {ln}\r\n\r\n{con}'.format(ln=len(cont), con=cont))
                            
                    elif client_flag: # It's done... The client program was already sent.
                        pass
                        
                    else: # normal:
                        send_status(path, status, client_socket, last_update, name) # last update and name may be None or not None - if they are not None - it will be "noticed" in send_status() and will be handled appropriately (public folder download phase 1). 
        
        
def make_threads_and_queue(num, size):
    ''' This method makes 'num' Thread waiting to take tasks from a Queue in size 'size'.
    '''
    global q
    q = Queue.Queue(size)
    for i in xrange(num):
        t = Thread(target=do_work)
        t.deamon = True
        t.start()


## Main Activity Method: ##
def run():
    ''' Runs the server.
    '''
    port = 80
    make_threads_and_queue(NUM_OF_THREADS, SIZE_OF_QUEUE)
    server_socket = socket.socket()
    while True: # Take the first free port after 80 [if it's not free]:
        try:
            server_socket.bind(('0.0.0.0', port))
            break
        except:
            port+=1
    server_socket.listen(6)
    print "Running... on port {}".format(port) # -For The Record-

    while True:
        client_socket, client_addr = server_socket.accept();    print "A client accepted" # -For The Record-
        q.put((client_socket, client_addr))


'''
Exciting. Satisfying. Period.
.
'''
