import socket
import base64
import os

HOST_N = socket.gethostname()
HOST, PORT = socket.gethostbyname(HOST_N), 10080

print(HOST)

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP) 
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print('Serving HTTP on port %s ...' % PORT)
while True:
    client_connection, client_address = listen_socket.accept()
    request = client_connection.recv(1024)
    option = request.decode().split(' ')
    print(request)

    if option[1]:

        if option[1]=='/success.jpg':

            with open("success.jpg", "r+b") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                size = str(os.path.getsize("success.jpg"))

                HTTP_RESPONSE = b'\r\n'.join([
                b"HTTP/1.1 200 OK",
                b"Connection: close",
                b"Content-Type: image/jpg",
                bytes("Content-Length: %s" % len(encoded_string),'utf-8'),
                b'', encoded_string 
] )

                print(HTTP_RESPONSE)
                client_connection.sendall(HTTP_RESPONSE.encode('ASCII'))



        else:

            with open("404.jpg", "r+b") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                size = str(os.path.getsize("404.jpg"))

                HTTP_RESPONSE = "HTTP/1.1 200 OK\n" + "Connection: close\n" + "Content-Type: image/jpg\n" + "Content-Lenght: "+ size + "\n\n" + str(encoded_string)

                client_connection.sendto(HTTP_RESPONSE.encode('ASCII'), (HOST, PORT))

    else:
        pass    

    client_connection.close()