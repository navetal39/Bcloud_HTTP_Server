# INFO: #
# ===================================

# Constants: #
## Pahts: ##
### Error paths: ###
ERROR_404_PATH = "Pages/Error404.htm"
ERROR_405_PATH = "Pages/Error405.htm"
ERROR_500_PATH = "Pages/Error500.htm"
NO_NAME_ERROR_PATH = "Pages/ErrorNoName.htm"
EMPTY_FOLDER_ERROR_PATH = "Pages/ErrorEmptyFolder.htm"
NAME_IN_USE_ERROR_PATH = "Pages/ErrorNameInUse.htm"
### General paths: ###
LAST_UPDATE_PLUS_PATH = "Pages/LastUpdatePlus.htm"
SIGN_UP_APPROVAL_PATH = "Pages/SignUpApproval.htm"
## Server-Server Communication: ##
from COM import MAIN_SERVER_PORT, MAIN_SERVER_IP


# Imports: #
import socket
from Main_Server_Com import *
from os.path import isfile


def get_server_for_thread():
    return Server(MAIN_SERVER_IP, MAIN_SERVER_PORT)
    
def get_fields_values(cont):
    ''' Receives a url parameters format string - returns a dictionary containing key for each parameter that will refer to it's value. 
    '''
    fields_values = dict()
    fields = cont.split('&') # Parameters are separated by an ampersand ('&').
    for field in fields:
        name, value = field.split('=') # The parameter's name is separated from it's value by an equal sign ('=').
        fields_values[name] = value

    return fields_values

def path_exists(path):
    ''' For conventions, :P.
    '''
    return isfile(path)

def download_or_register(main_server, params):
    ''' This method receives the url parameter and according to them determines whether it is: the public folder download first phase, the public folder download second phase or registry request.
    Then it deals with the request appropriately (mostly passes the mission on to the correct place), checks the returned status and informs the HTTP server accordingly with the appropriate path and status code [and a flag (folder_flag) and some data (username and last_update)].
    '''
    folder_flag = False # Flag - to return to HTTP server so he'll know what phase is it.
    last_update = None # So that if it will be assigned - there will be no error.
    try:
        params_dict = get_fields_values(params)
    except: # 500 Internal Server Error
        raise
    
    if len(params_dict.keys()) == 1 and "username" in params_dict.keys(): # Download - phase 1 - get public folder last update:
        name = params_dict["username"]
        stat, data = main_server.get_last_update(name, 'public')
		# The possible statuses (NNM=No Name, EMP=Empty Folder, SCS=Success) are checked: #
        if stat == "NNM":
            path = NO_NAME_ERROR_PATH
            status = "200"
        elif stat == "EMP":
            path = EMPTY_FOLDER_ERROR_PATH
            status = "200"
        elif stat == "SCS":
            path = LAST_UPDATE_PLUS_PATH
            status = "200"
            last_update = data
        
    elif len(params_dict.keys()) == 2 and "username" in params_dict.keys() and "is_approved" in params_dict.keys() : # Download - phase 2 - check whether the user still wants to download, if he does tell that to HTTP server:
        value = params_dict["is_approved"]
        # Check the client's answer: # 
        if value == "YES":
            folder_flag = True
            path = ""; status = "" # Just in case
        elif value == "NO":
            path = ""; status = ""  # Just in case
        else: # If the user decides to try to be funny and put something else in the url rather than "YES/NO" thinking that he may crash our server by doing so...
            status = "404"
            path = ERROR_404_PATH

    elif (len(params_dict.keys()) == 2) and ("username" in params_dict.keys()) and ("password" in params_dict.keys()) : # Sign Up:
        status, path = register(main_server, params_dict)
        


    else: # Same thing again... If the user decides to try to be funny and put something else in the url rather than "username"/"is_approved"/"password" thinking that he may crash our server by doing so...
        status = "404"
        path = ERROR_404_PATH
        
    return status, path, folder_flag, params_dict["username"], last_update

def register(main_server, fields_dict):
    ''' The method asks the main server to register the client (according to the details in the parameter) - then it checks the status returned and informs the HTTP server accordingly with the appropriate path and status code.
    '''
    stat = main_server.create_user(fields_dict['username'],  fields_dict['password'])
	# The possible statuses (NIU=Name In Use, SCS=Success) are checked: #
    if stat == "NIU":
        path = NAME_IN_USE_ERROR_PATH
        status = "200"
    elif stat == "SCS":
        path = SIGN_UP_APPROVAL_PATH
        status = "200"
    else: # 500 Internal Server Error
        raise
		
    return status, path

def get_folder(main_server, name):
    ''' Get the zipped folder from the main_server.
    '''
    return main_server.get_folder(name)


'''
Exciting. Satisfying. Period.
.
'''
