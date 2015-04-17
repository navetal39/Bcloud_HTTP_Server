# INFO: #
# ===================================


# File Transfering: #
def file_recv(sock, count = 0):
    ''' This method is for reciving large files.
    '''
    response = sock.recv(2048)
    print 'recived '+response # -For The Record-
    flag, str_size = response.split('|')
    try:
        if flag != 'SIZ':
            raise
        size = int(str_size)
    except:
        if count < 3: #Just making sure that it won't attemt endlessly
            print 'try again' # -For The Record-
            sock.send('NAK|'+response)
            final_response = file_recv(sock, count+1)
        else:
            final_response = 'WTF'
    else:
        sock.send('ACK|'+response)
        print 'go for it' # -For The Record-
        final_response = sock.recv(size)
        print 'recived file' # -For The Record-
    finally:
        return final_response

def file_send(sock, mess):
    ''' This method is for sending large files.
    '''
    size = len(mess)
    size_message = 'SIZ|{}'.format(size)
    print 'sending '+size_message # -For The Record-
    sock.send('SIZ|{}'.format(size))
    response = sock.recv(len(size_message) + 5)
    print 'recived '+response # -For The Record-
    response_parts = response.split('|')
    flag = response_parts[0]; response_parts.remove(flag)
    if response_parts == size_message.split('|'):
        if flag == 'NAK':
            print 'trying again' # -For The Record-
            file_send(sock, mess)
            return
        elif flag == 'ACK':
            sock.send(mess)
            print 'sent mess' # -For The Record-
        else: #Just so there'll be an else...
            pass
    else:
        print response_parts
        print size_message.split('|')

'''
Exciting. Satisfying. Period.
.
'''
