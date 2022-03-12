import socket
import threading
import os
import time


def run_server(host, port, dir, v):
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
            useful_data = decoded_data.split(" HTTP/")[0]
            print(decoded_data)

            if 'GET /' in useful_data:
                get_request(conn, useful_data, dir, v)
                break

            if 'POST /' in useful_data:
                post_request(conn, useful_data, dir, v)
                break

    except FileNotFoundError:
        response = http_response(404, 0)
        response = response.encode("utf-8")
        conn.sendall(response)
        if v:
            print(response)

    except PermissionError:
        response = http_response(403, 0)
        response = response.encode("utf-8")
        conn.sendall(response)
        if v:
            print(response)

    except OSError:
        response = http_response(400, 0)
        response = response.encode("utf-8")
        conn.sendall(response)
        if v:
            print(response)


    finally:
        print('Client from', addr, 'has disconnected')
        conn.close()


def get_request(conn, useful_data, dir, v):
    useful_data = useful_data.replace("%20", " ")
    response = ""
    content = ""
    if dir and len(dir) > 1:
        directory = dir + "/"
    else:
        directory = ""

    if "d=" in useful_data:
        directory = directory + "." + useful_data.split("d=")[1]
    else:
        directory = directory + '.'

    folder = os.listdir(directory)

    if len(useful_data) > 5:
        file_requested = useful_data.split("/")[1]
        file_requested = file_requested.split("?")[0]

        if "-d" in file_requested:
            file_requested = file_requested.split("d=")[0]

        for f in folder:
            file_name = f.split('.')[0]
            if f.startswith(file_requested) and file_requested == file_name:
                f = open(directory + "/" + f, 'r')
                content = f.read()
                break
            else:
                content = "404"

        if "404" in content:
            response = http_response(404, 0) + "<html><body><p>"
            content = ""
        else:
            response = http_response(200, len(content)) + "<html><body><p>"

    elif len(useful_data) == 5:
        all_files = ""
        for f in folder:
            if f == "HTTP_Server.py":
                continue
            else:
                all_files += "/" + f + "<br />"
        content += all_files

    response = http_response(200, len(content)) + "<html><body><p>"
    response += content
    response = response.encode("utf-8")
    conn.sendall(response)
    if v:
        print(response)


def post_request(conn, useful_data, dir, v):
    content = ""
    file_requested = ""
    if dir and len(dir) > 1:
        directory = dir + "/"
    else:
        directory = ""

    if "d=" in useful_data:
        directory = directory + "." + useful_data.split("d=")[1]
        file_requested = useful_data.split("/")[1]
        file_requested = file_requested.split("?")[0]

        if "c=" in useful_data:
            directory = directory.split("&")[0]
            content = useful_data.split("c=")[1]
            content = content.replace("%20", " ")
            content = content.replace("+", " ")
    else:
        directory = directory + '.'
        file_requested = useful_data.split("/")[1]

        if "c=" in useful_data:
            file_requested = file_requested.split("?")[0]
            content = useful_data.split("c=")[1]
            content = content.replace("%20", " ")
            content = content.replace("+", " ")

    if os.path.isfile(directory + "/" + file_requested):
        output_file = open(directory + "/" + file_requested, 'w')
        output_file.write(content)
        return_message = "File Overwritten<br />" + content
    else:
        output_file = open(directory + "/" + file_requested, 'w')
        output_file.write(content)
        return_message = "New File Created<br />" + content

    response = http_response(200, len(return_message)) + "<html><body><p>"
    response += return_message + "</p></body></html>"
    response = response.encode("utf-8")
    conn.sendall(response)
    if v:
        print(response)


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
                + "Content-Length: " + str(length) + " ." \
                + "Content-Type: text/html\r\n" \
                + "\r\n"

    modified_http_response = response.replace("\r\n", "<br />")
    modified_http_response = modified_http_response.replace(" .", "<br />")
    response += modified_http_response

    return response
