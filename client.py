import socket
import os
import json
import base64

if __name__ == "__main__":
    host = 'localhost'
    port = 12000

    save_directory = "client_files"

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    
    

    # file transfer
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        file_name = input("Enter filename you want to transfer: ")
        file_path = os.path.join(save_directory, file_name)

        try:
            with open(file_path, 'rb') as fi:  # Open file in binary mode
                chunk_index = 0
                while True:
                    file_data = fi.read(1024)  # Read data in chunks
                    if not file_data:
                        break #if not more data to read file transfer is complete
                    
                    # encoding chunks as base64 and  preparing json message
                    file_data_base64 = base64.b64encode(file_data).decode('utf-8')

                    json_message = {
                        "file_name": file_name if chunk_index == 0 else "",  #send filename only in the first chunk
                        "chunk_index": chunk_index,
                        "file_data": file_data_base64
                    }

                    sock.sendall(json.dumps(json_message).encode('utf-8')+ b"\n")  #send json with newline as delimiter
                    chunk_index += 1

            print(f"File '{file_name}' sent successfully.")
    
        # except IOError:
        #     print("You entered an invalid filename! Please try again...")

        except Exception as e:
            print(f"error: {e}")

        x = input("are you receriving another file: ")
        if x != "y" :
            break
    sock.close()