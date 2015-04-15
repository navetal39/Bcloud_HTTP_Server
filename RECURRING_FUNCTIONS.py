# INFO: #
# ===================================

'''
TO DO:
1) secured functions
'''

import crypto

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
    response = sock.recv(2048)
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




# Secure communication #:
def secure_recv(sock, size = 2048):
    ''' This method receives the encrypted message (the ciphertext), decrypts it and returns the plaintext (NOT SSL/TLS).
    '''
    encMess = sock.recv(size)
    mess = crypto.decrypt(encMess)
    return mess

def secure_send(sock, mess):
    ''' This method gets the message (the plaintext), encrypts it and sends it (the ciphertext) (NOT SSL/TLS).
    '''
    print "sending {m}".format(m=mess) # -For The Record-
    encMess = crypto.encrypt(mess)
    sock.send(encMess)
    

## Files: ##
def secure_file_recv(sock, count = 0):
    ''' This method is for reciving large files.
    '''
    response = secure_recv(sock)
    print 'recived '+response # -For The Record-
    flag, str_size = response.split('|')
    try:
        if flag != 'SIZ':
            raise
        size = int(str_size)
    except:
        if count < 3: #Just making sure that it won't attemt endlessly
            print 'try again' # -For The Record-
            seure_send(sock, 'NAK|'+response)
            final_response = secure_file_recv(sock, count+1)
        else:
            final_response = 'WTF'
    else:
        secure_send(sock, 'ACK|'+response)
        print 'go for it' # -For The Record-
        final_response = secure_recv(sock, size)
        print 'recived file' # -For The Record-
    finally:
        return final_response

def secure_file_send(sock, mess):
    ''' This method is for sending large files.
    '''
    size = len(mess)
    size_message = 'SIZ|{}'.format(size)
    print 'sending '+size_message # -For The Record-
    secure_send(sock, size_message)
    response = sock.recv(2048) #Isn't that supposed to be secure_recv()?
    print 'recived '+response # -For The Record-
    response_parts = response.split('|')
    flag = response_parts[0]; response_parts.remove(flag)
    if flag == 'NAK':
        print 'trying again' # -For The Record-
        secure_file_send(sock, mess)
        return
    elif flag == 'ACK':
        secure_send(sock, mess)
        print 'sent mess' # -For The Record-
    else: #Just so there'll be an else...
        pass



'''
Exciting. Satisfying. Period.
.
'''
