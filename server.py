import socket 
import os
import json
import base64

if __name__ == "__main__":
    host = 'localhost'
    port = 12000

    totalclients = 1

    # diretory for saving files 
    save_directory = "server_files"

    # making directory if the directory does not exist
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(totalclients)

    print("waiting for clients...")
    clientsocket, address = server.accept()
    print(f"Connected with {address} client...")

    # initializing variables
    file_name = None
    file_path = None

    while True:
        # receive file in chunks
        with clientsocket.makefile('r') as client_file: #wrap soket in the file for line based reading 
            for line in client_file:
                message = json.loads(line.strip()) #parsing each json line

                #get file name only once in the first chunk
                if not file_name and message["file_name"]:
                    file_name = message["file_name"]
                    file_path = os.path.join(save_directory, file_name)

                #decode base64 data and write it to the file
                file_data = base64.b64decode(message["file_data"])
                with open(file_path, "ab") as fo:  #append binary data to the file
                    fo.write(file_data)
                    
        print(f"file {file_name} received succesfully! from the client: {address}")

        clientsocket.close()