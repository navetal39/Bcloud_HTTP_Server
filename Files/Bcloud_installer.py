import socket, os, zipfile

http_ip = '127.0.0.1'
sync_ip = '127.0.0.1'
http_port = 81
sync_port = 5126

# Get data from server
sock = socket.socket()
sock.connect((http_ip, http_port))
sock.send("GET /Files/client.zip HTTP/1.1\r\n\r\n")
print "Downloading client..."
cont_len = sock.recv(5000)
int_len = int(cont_len)
sock.send('ACK')
zip_cont = sock.recv(int_len)
sock.close()
print "Got data"

# Get info from user
while True:
    program_location = raw_input("Enter the path for the directory in which you wish to put the program's files: ")
    if not os.path.exists(program_location):
        print "PATH DOES NOT EXIST."
    else:
        program_location += '/BcloudFiles'
        os.makedirs(program_location)
        break
while True:
    sync_location = raw_input("Enter the path for the directory in which you wish to put the Bcloud directory (for sync): ")
    if not os.path.exists(sync_location):
        print "PATH DOES NOT EXIST."
    else:
        break
while True:
    sync_time = raw_input("Enter the amount of time you wish to have between syncs, in seconds: ")
    try:
        int(sync_time)
        if sync_time < 10:
            raise ValueError
    except ValueError:
        print "The input must be an intiger, at least 10!"
    else:
        break

# Extract data into location
zip_file = open(program_location + '/temp.zip', 'wb')
zip_file.write(zip_cont)
zip_file.close()
zip_file = zipfile.ZipFile(program_location + '/temp.zip', 'r', zipfile.ZIP_DEFLATED)
zip_file.extractall(program_location)
zip_file.close()
os.remove(program_location+"/temp.zip")

# Edit config
config = open(program_location + '/config.py', 'w')
config.write("SYNC_IP = '{}'\nSYNC_PORT = {}\nFOLDERS_LOCATION = '{}'\nTIME_BETWEEN_SYNCS = {}".format(sync_ip, sync_port, sync_location, sync_time))
config.close()

print 'Bcloud has been installed successfully'
raw_input('Press enter to continue...')
