import socket
import os
import json
import base64

# host = '192.168.249.150'
host = 'localhost'
# host = socket.gethostbyname(socket.gethostname())

port = 13345

save_directory = "./client_files"

def send_file(file_name):
    file_path = os.path.join(save_directory, file_name)
    # file_path = os.path.join(save_directory, file_name)
    try:  
        # Establish the connection to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        action_message = {
           "action": "send",
           "file_name": file_name
        }
        client_socket.sendall(json.dumps(action_message).encode('utf-8')+ b"\n")

        print(f"Sending file '{file_name}' to server... ")
        with open(file_path, 'rb') as fi:  # Open file in binary mode
            chunk_index = 0
            while True:
                file_data = fi.read(1024)  # Read data in chunks
                if not file_data:
                    break #if not more data to read file transfer is complete
                
                # encoding chunks as base64 and  preparing json message
                file_data_base64 = base64.b64encode(file_data).decode('utf-8')

                data_message = {
                    "file_name": file_name if chunk_index == 0 else "",  #send filename only in the first chunk
                    "chunk_index": chunk_index,
                    "file_data": file_data_base64
                }

                client_socket.sendall(json.dumps(data_message).encode('utf-8')+ b"\n")  #send json with newline as delimiter
                chunk_index += 1

        end_file_flag = {
            "status": "end_transfer",
            "file_name": file_name
        }

        client_socket.sendall(json.dumps(end_file_flag).encode('utf-8') + b"\n")
        print(f"File '{file_name}' sent successfully.")


    except Exception as e:
        print(f"Error sending file: {e}")

    finally:
        client_socket.close()
        print("returning to main menu...\n")

def request_file(file_name):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        action_message = {
            "action": "request",
            "file_name": file_name
        }
        client_socket.sendall(json.dumps(action_message).encode('utf-8') + b"\n")

        file_path = os.path.join(save_directory, file_name)
        print(f"Receiving file '{file_name}' from server... ")
        with open(file_path, "wb") as fo:
            buffer = ""
            while True:
                response = client_socket.recv(1024)
                if not response:
                    break

                # Accumulate buffer until newline is found
                buffer += response.decode()
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    message = json.loads(line.strip())

                    if message.get("status") == "end_transfer":
                        print(f"File '{file_name}' received successfully.")
                        # return
                        break

                    file_data = base64.b64decode(message["file_data"])
                    fo.write(file_data)

    except Exception as e:
        print(f"Error receiving file: {e}")

    finally:
        client_socket.close()
        print("\nreturning to main menu...\n")

def view_files_list():
    try:
        #establish the connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        print("connecting to the server...")
        print("requesting available files list from the server...")

        #sending the action
        action_message = {
            "action" : "available_file_list"
        }

        client_socket.sendall(json.dumps(action_message).encode('utf-8') + b"\n")

        #receiving the files list
        data_buffer = ""
        while True:
            #receive data in 1024 chunks
            chunk = client_socket.recv(1024).decode('utf-8')
            if not chunk:
                break #exit if there are no more data

            data_buffer += chunk

            #check if we reached to the end of the message
            if '\n' in data_buffer:
                #extract the full message before the newline
                full_message, data_buffer = data_buffer.split('\n', 1)

                message = json.loads(full_message)

                #confirm the the received message the right one by checking the action is list
                if message.get("action") == "list":
                    files_list = message.get("files_list", [])
                
                    if files_list:
                        print("\nAvailable files list on the server: ")
                        for file in files_list:
                            print(f"- {file}")
                        break
                    else:
                        print("No files available on the server.")
                return  #exit


    except Exception as e:
        print(f"Error receiving list: {e}")
    
    finally:
        client_socket.close()
        print("\nreturning to main menu...\n")




if __name__ == "__main__":
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    while True:
        print("============================================")
        print("       P2P FILE TRANSFER APPLICATION        ")
        print("============================================")
        print("\nOptions:")
        print("1. Upload a file to the server")
        print("2. Download a file from the server")
        print("3. view available files in the server.")
        print("4. exit.")
        choice = input("Enter choice (1 , 2, 3 or 4): ")

        if choice == "1":
            print("\n============================================")
            print("\n           UPLOADING CENTER\n")
            available_client_files = os.listdir(save_directory)
            if available_client_files:
                print("Available files to upload:")
                for file in available_client_files:
                    print(f"- {file}")
            else:
                print("No files exist to upload.")
                
                continue

            file_name = input("\nEnter filename you want to send: ")
            file_path = os.path.join(save_directory, file_name)
            if os.path.isfile(file_path):
                send_file(file_name)
                print("\nreturning to main menu...\n")
                continue
            else:
                print(f"\n'{file_name}' file does not exist.")
                print("\nreturning to main menu...\n")
                continue
        elif choice == "2":
            print("\n============================================")
            print("\n          DOWNLOADING CENTER\n")
            view_files_list()
            file_name = input("Enter the file name to request from server: ")
            request_file(file_name)
            continue

        elif choice == "3":
            view_files_list()
            continue

        elif choice == "4":
            break

        else:
            print("Invalid choice.")
            print("\nreturning to main menu...\n")
            continue
