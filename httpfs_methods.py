import socket
import threading
import os
import time

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

    target_file = method_path_data.split()[1].split("/")[-1]
    full_path = method_path_data.split()[1].strip("/")
    folder_path = ""
    files = os.listdir(dir)
    content = ""

    if "../" in full_path:
        content = "400"
    elif full_path == '/' or full_path == "":
        for f in files:
            if f == "httpfs.py" or f == "httpfs_methods.py":
                continue
            else:
                content += f + '\n'
    else:
        if "/" in full_path:
            split_path = full_path.split("/")
            folder_path = ""
            for i in range(len(split_path)):
                if "." not in split_path[i]:
                    folder_path = folder_path + split_path[i]
            files = os.listdir(folder_path)
        if target_file in files:
            filer = open(dir + '/' + full_path, 'r')
            content = filer.read() + '\n'
            filer.close()
        else:
            content = "404"

    if "404" in content:
        response = generate_response(404, 0)
        if v:
            print("Returning an error message to the client:")
    elif "400" in content:
        response = generate_response(400, 0)
        if v:
            print("Returning an error message to the client:")
    else:
        response = generate_response(200, len(content))
        response += content
        if v:
            print("Returning the requested data to the client:")
    conn.sendall(response.encode('utf-8'))
    if v:
        print(response)
    conn.close()
    print()


def post_request(conn, method_path_data, decoded_data, dir, v):
    target_file = method_path_data.split()[1].split("/")[-1]
    full_path = method_path_data.split()[1].strip("/")
    folder_path = ""
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
            split_path = full_path.split("/")
            folder_path = ""
            for i in range(len(split_path)):
                if "." not in split_path[i]:
                    folder_path = folder_path + split_path[i]
            files = os.listdir(folder_path)
        if target_file in files:
            if v:
                print('Overwriting file at ', full_path)
                print()
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
        response = generate_response(403, 0)
        if v:
            print("Returning an error message to the client:")
    elif "400" in response_msg:
        response = generate_response(400, 0)
        if v:
            print("Returning an error message to the client:")
    else:
        response = generate_response(200, len(response_msg))
        response += response_msg
        if v:
            print("Returning a response message to the client:")
    conn.sendall(response.encode('utf-8'))
    if v:
        print(response)
    conn.close()
    print()


def generate_response(code, length):
    current_time = time.strftime("%c")

    if code == 200:
        response = "HTTP/1.1 200 OK\r\n"

    elif code == 404:
        response = "HTTP/1.1 404 Not Found\r\n"

    elif code == 400:
        response = "HTTP/1.1 400 Bad Request\r\n"

    elif code == 403:
        response = "HTTP/1.1 403 Forbidden\r\n"

    response += "Date: " + current_time + "\r\n" \
                + "Content-Type: text/html\r\n" \
                + "Content-Length: " + str(length) + "\r\n" \
                + "\r\n"

    return response
