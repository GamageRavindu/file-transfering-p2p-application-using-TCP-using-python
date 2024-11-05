import socket
import os


if __name__ == "__main__":
    host = 'localhost'
    port = 12000

    save_directory = "client_files"

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # file transfer
    while True:
        file_name = input("Enter filename you want to transfer: ")
        file_path = os.path.join(save_directory, file_name)

        try:
            with open(file_path, 'rb') as fi:  # Open file in binary mode
                data = fi.read(1024)  # Read data in chunks
                while data:
                    sock.send(data)  # Send binary data directly
                    data = fi.read(1024)  # Read the next chunk
            print(f"File '{file_name}' sent successfully.")
            break
        except IOError:
            print("You entered an invalid filename! Please try again...")
