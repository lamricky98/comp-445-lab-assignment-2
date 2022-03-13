import socket
import threading
import os
import time
import re

def run_server(host, port, dir, v):
    if dir is None or dir == "":
        dir = os.path.dirname(os.path.realpath(__file__))

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.bind((host, port))
        listener.listen(5)
        print('Server is listening at port', port)
        while True:
            conn, addr = listener.accept()
            threading.Thread(target=handle_client, args=(conn, addr, dir, v)).start()
    finally:
        listener.close()


def handle_client(conn, addr, dir, v):
    print('New client from', addr)
    try:
        while True:
            data = conn.recv(1024)
            decoded_data = data.decode("utf-8")
            method_path_data = decoded_data.split(" HTTP/")[0]
            if v:
                print("Printing request message:")
            print(decoded_data)

            if 'GET /' in method_path_data:
                get_request(conn, method_path_data, dir, v)
                break

            if 'POST /' in method_path_data:
                post_request(conn, method_path_data, decoded_data, dir, v)
                break
    finally:
        print('Client from', addr, 'has disconnected')
        conn.close()


def get_request(conn, method_path_data, dir, v):
    response = ""

    files = os.listdir(dir)
    path = method_path_data.split()[1]
    content = ""

    if "../" in path:
        content = "400"
    elif path == '/':
        for f in files:
            if f == "httpfs.py" or f == "httpfs_methods.py":
                continue
            else:
                content += f + '\n'
    elif re.search(r'\/\w+.\w+', path):
        path = path.strip('/')
        if path in files:
            filer = open(dir + '/' + path, 'r')
            content = filer.read() + '\n'
            filer.close()
        else:
            content = "404"

    if "404" in content:
        response = http_response(404, 0)
        print("Returning an error message to the client:")
    elif "400" in content:
        response = http_response(400, 0)
        print("Returning an error message to the client:")
    else:
        response = http_response(200, len(content))
        response += content
        print("Returning the requested data to the client:")
    conn.sendall(response.encode('utf-8'))
    if v:
        print(response)
    conn.close()
    print()


def post_request(conn, method_path_data, decoded_data, dir, v):
    target_file = method_path_data.split()[1].split("/")[-1]
    full_path = method_path_data.split()[1]
    path = method_path_data.split()[1]
    files = os.listdir(dir)

    rq = decoded_data.split('\r\n')
    index = rq.index('')
    rq_data = ''
    for l in rq[index + 1:]:
        rq_data += l + '\n'

    if "../" in full_path:
        response_msg = "400"
    else:
        if "/" in full_path:
            while "/" in path and "." not in path:
                path = path.split("/")[1]
                files = os.listdir(path.split("/")[0])
        if target_file in files:
            if v:
                print('Overwriting file at ', full_path)
            filer = open(dir + '/' + full_path, 'w+')
            filer.write(rq_data)
            filer.close()
            response_msg = 'Data overwritten to file ' + full_path
        elif target_file not in files:
            if v:
                print('Writing new file at', full_path)
                print()
            filer = open(dir + '/' + full_path, 'w+')
            filer.write(rq_data)
            filer.close()
            response_msg = 'Data written to new file ' + full_path
        else:
            response_msg = "403"

    if "403" in response_msg:
        response = http_response(403, 0)
        print("Returning an error message to the client:")
    elif "400" in response_msg:
        response = http_response(400, 0)
        print("Returning an error message to the client:")
    else:
        response = http_response(200, len(response_msg))
        response += response_msg
        print("Returning a response message to the client:")
    conn.sendall(response.encode('utf-8'))
    if v:
        print(response)
    conn.close()
    print()


def http_response(number, length):
    now = time.strftime("%c")

    if number == 200:
        response = "HTTP/1.1 200 OK\r\n"

    elif number == 404:
        response = "HTTP/1.1 404 Not Found\r\n"

    elif number == 400:
        response = "HTTP/1.1 400 Bad Request\r\n"

    elif number == 403:
        response = "HTTP/1.1 403 Forbidden\r\n"

    response += "Date: " + now + "\r\n" \
                + "Content-Type: text/html\r\n" \
                + "Content-Length: " + str(length) + "\r\n" \
                + "\r\n"

    return response
