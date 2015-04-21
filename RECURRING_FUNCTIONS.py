# INFO: #
# ===================================


# File Transfering: #
def file_recv(sock, count = 0):
    ''' This method is for receiving large files. It works according to BCF Protocol, which is documented on its own file in Hebrew.
    '''
    response = sock.recv(2048)
    print 'recived '+response # -For The Record-
    flag, str_size = response.split('|')
    try:
        if flag != 'SIZ':
            raise
        size = int(str_size)
    except: # Something went wrong, try again:
        if count < 3: # Just making sure that it won't attempt endlessly
            print 'try again' # -For The Record-
            sock.send('NAK|'+response) # Tell the other side I didn't received the size.
            final_response = file_recv(sock, count+1)
        else: # Something went wrong and we already tried again - really WTF:
            final_response = 'WTF'
    else: # The size was correctly received, now its time for the file:
        sock.send('ACK|'+response) # Tell the other side I got the size.
        print 'go for it' # -For The Record-
        final_response = sock.recv(size) # Now the file!
        print 'recived file' # -For The Record-
    finally:
        return final_response

def file_send(sock, mess):
    ''' This method is for sending large files. It works according to BCF Protocol, which is documented on its own file in Hebrew.
    '''
    size = len(mess)
    size_message = 'SIZ|{}'.format(size)
    print 'sending '+size_message # -For The Record-
    sock.send('SIZ|{}'.format(size)) # Send the size.
    response = sock.recv(len(size_message) + 5) # receive the status message.
    print 'recived '+response # -For The Record-
    response_parts = response.split('|')
    flag = response_parts[0]; response_parts.remove(flag)
    if response_parts == size_message.split('|'):
        if flag == 'NAK': # Something went wrong, try again:
            print 'trying again' # -For The Record-
            file_send(sock, mess)
            return
        elif flag == 'ACK': # LG! send the file:
            sock.send(mess)
            print 'sent mess' # -For The Record-
        else: # Just so there'll be an else...
            pass
    else:
        print response_parts
        print size_message.split('|')

'''
Exciting. Satisfying. Period.
.
'''
