import socket
import json
import traceback

# Define hosts and ports
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# Create listener
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((SERVER_HOST, SERVER_PORT))
server.listen(1)
print("Listening on port %s ..." % SERVER_PORT)


def get(param):
    if param == "freq":
        client.sendall(b"f\n")
        data = client.recv(1024).decode("utf-8").rstrip("\n")
        ret = json.dumps({"param": param, "value": data})
    elif param == "demod":
        client.sendall(b"m\n")
        data = client.recv(1024).decode("utf-8").rstrip("\n")
        ret = json.dumps({"param": param, "value": data.splitlines()[0]})
    elif param == "passband":
        client.sendall(b"m\n")
        data = client.recv(1024).decode("utf-8").rstrip("\n")
        ret = json.dumps({"param": param, "value": data.splitlines()[1]})
    elif param == "strength":
        client.sendall(b"l STRENGTH\n")
        data = client.recv(1024).decode("utf-8").rstrip("\n")
        ret = json.dumps({"param": param, "value": data})
    elif param == "sql":
        client.sendall(b"l SQL\n")
        data = client.recv(1024).decode("utf-8").rstrip("\n")
        ret = json.dumps({"param": param, "value": data})
    else:
        ret = "Invalid GET"
    return ret


def set(param, value):
    if param == "freq":
        client.sendall(bytes("F " + value, encoding="utf-8"))
        data = client.recv(1024).decode("utf-8").rstrip("\n")
        ret = json.dumps({"param": param, "response": data})
    elif param == "demod":
        client.sendall(bytes("M " + value, encoding="utf-8"))
        data = client.recv(1024).decode("utf-8").rstrip("\n")
        ret = json.dumps({"param": param, "value": data})
    elif param == "passband":
        client.sendall(b"m\n")
        mode = client.recv(1024).decode("utf-8").rstrip("\n").splitlines()[0]
        client.sendall(bytes("M " + mode + " " + value, encoding="utf-8"))
        data = client.recv(1024).decode("utf-8").rstrip("\n")
        ret = json.dumps({"param": param, "value": data})
    elif param == "sql":
        client.sendall(bytes("L SQL " + value, encoding="utf-8"))
        data = client.recv(1024).decode("utf-8").rstrip("\n")
        ret = json.dumps({"param": param, "value": data})
    else:
        ret = "Invalid SET"
    return ret


while True:
    client_connection, client_address = server.accept()
    try:freq
        request = client_connection.recv(1024).decode()
        request = request.split("\r\n")
        data = json.loads(request.pop())
        if request[0] == "POST /connect HTTP/1.1":
            print(str(data["gqrx_ip"]))
            print(str(data["gqrx_port"]))
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((data["gqrx_ip"], int(data["gqrx_port"])))
                print("Connected")
                response = "HTTP/1.0 200 OK\n\nConnected"
            except Exception:
                if "already connected" in traceback.format_exc():
                    response = "HTTP/1.0 400 Bad Request\n\nAlready Connected!"
                else:
                    response = "HTTP/1.0 400 Bad Request\n\nFailed to connect. Ensure that remote control is enabled in GQRX"
                traceback.print_exc()

        elif request[0] == "POST /disconnect HTTP/1.1":
            client.close()
            print("Disconnected")
            response = "HTTP/1.0 200 OK\n\nDisconnected"

        elif request[0] == "GET /get HTTP/1.1":
            r = get(data["param"])
            print("GET: " + r)
            response = "HTTP/1.0 200 OK\n\n" + str(r)

        elif request[0] == "POST /set HTTP/1.1":
            r = set(data["param"], data["value"])
            print("SET: " + r)
            response = "HTTP/1.0 200 OK\n\n" + str(r)
        else:
            response = "HTTP/1.0 400 Bad Request\n\n"

    except Exception:
        response = "HTTP/1.0 400 Bad Request\n\nInvalid request. Ensure request is GET or POST, JSON is being sent and JSON is correctly formatted. Full exception printed to console."
        traceback.print_exc()
    # Send HTTP response
    client_connection.sendall(response.encode())
    client_connection.close()

# Close sockets on exit
server.close()

s.sendall(b"f\n")
data = s.recv(1024)
s.close()
print("Received", repr(data))
