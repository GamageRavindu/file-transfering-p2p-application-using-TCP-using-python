import socket
import threading
import os
import json
import base64

# Configure server host and port
serverHost = 'localhost'
serverPort = 12345
bufferSize = 4096

# Directory to store received files
save_directory = "server/server_files"
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

def handle_send_file(client_file, file_name):
    
    file_path = os.path.join(save_directory, file_name)
    print(f"Receiving file '{file_name}' from client... ")
    with open(file_path, "wb") as fo:  # Open file in write-binary mode
        for line in client_file:
            message = json.loads(line.strip())

            # Check for end of transfer
            if message.get("status") == "end_transfer":
                print(f"File '{file_name}' received successfully.")
                return  # End the file transfer

            # Decode base64 data and write to file
            file_data = base64.b64decode(message["file_data"])
            fo.write(file_data)

def handle_request_file(clientsocket, file_name, save_directory):
    
    file_path = os.path.join(save_directory, file_name)

    if not os.path.isfile(file_path):
        print(f"File '{file_name}'is not found.")
        error_message = {"status": "error", "message": "File not found"}
        clientsocket.sendall(json.dumps(error_message).encode('utf-8') + b"\n")
        return
    print(f"Sending file '{file_name}' to client...")
    with open(file_path, "rb") as fi:
        chunk_index = 0
        while True:
            file_data = fi.read(1024)  # Read file data in chunks
            if not file_data:
                break  # No more data to read; file transfer is complete

            # Encode the chunk in base64 and prepare the JSON message
            file_data_base64 = base64.b64encode(file_data).decode('utf-8')
            data_message = {
                "file_name": file_name if chunk_index == 0 else "",  # Send file name only in first chunk
                "chunk_index": chunk_index,
                "file_data": file_data_base64
            }
            clientsocket.sendall(json.dumps(data_message).encode('utf-8') + b"\n")
            chunk_index += 1

    # Send a message to indicate the end of the transfer
    end_message = {
        "status": "end_transfer", 
        "file_name": file_name
    }
    clientsocket.sendall(json.dumps(end_message).encode('utf-8') + b"\n")

    print(f"File '{file_name}' sent successfully to the client.")

def send_available_files(client_socket):
    listfile = os.listdir(save_directory)

    list_files = {
        "action": "list",
        "files_list": listfile
    }

    list_files_message = json.dumps(list_files).encode('utf-8') + b"\n"

    for i in range(0, len(list_files_message), 1024):
        client_socket.sendall(list_files_message[i:i+1024])
    
    print("list of available files send to client.")
    
     

# Handle client connection
def handleClient(clientsocket):
    file_name = None
    # file_path = None
    try:
        with clientsocket.makefile('r') as client_file:
            # Expect the first message to be an action message
            action_message = json.loads(client_file.readline().strip())
            action = action_message.get("action")
            file_name = action_message.get("file_name")

            if action == "send":
                handle_send_file(client_file, file_name)

            elif action == "request":
                handle_request_file(clientsocket, file_name, save_directory)

            elif action == "available_file_list":
                send_available_files(clientsocket)

            else:
                print("Unknown action received from client.")

    except Exception as e:
        print(f"Error handling client: {e}")
    
    finally:
        clientsocket.close()

# Start the server and listen for incoming connections
def startServer():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((serverHost, serverPort))
    server.listen()

    print(f"Server is listening on {serverHost}:{serverPort}")

    while True:
        clientSocket, address = server.accept()
        print(f"Connected by {address}")

        clientThread = threading.Thread(target=handleClient, args=(clientSocket,))
        clientThread.start()

if __name__ == "__main__":
    startServer()
