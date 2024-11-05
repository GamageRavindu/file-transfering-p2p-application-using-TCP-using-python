import socket 
import os

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

    filename = f"output.jpg"
    file_path = os.path.join(save_directory, filename)

    received_data_chunk = clientsocket.recv(1024) 
    with open(file_path, "wb") as fo:
        while received_data_chunk:
            fo.write(received_data_chunk)
            received_data_chunk = clientsocket.recv(1024)
    
    print("file received from client!")

    clientsocket.close()