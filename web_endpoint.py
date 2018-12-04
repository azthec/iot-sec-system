#!/usr/bin/env python

from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from ssl import wrap_socket
from datetime import datetime
from mysql import connector

# global variable setup
arduino_keys = {'1': "846HqXQ2xPD8TiMjTnshj0UETmxSpT",
                '2': "RadQXmgCJWHbV6YSnuEhObDN1XrYiL",
                '3': "t7XodejIrK35NQSdklCIjM7fyeKIx2"}
db_user = "arduino"
db_pass = "password"
db_name = "iotsec"

# reset table id and contents with: truncate table metrics;

# string to insert data row
add_metric = "INSERT INTO metrics " + \
             "(name, source, value, datetime) " + \
             "VALUES (%s, %s, %s, %s)"


try:
    cnx = connector.connect(user=db_user, password=db_pass,
                            host='127.0.0.1', database=db_name)
except connector.Error as err:
    if err.errno == connector.errorcode.ER_ACCESS_DENIED_ERROR:
        print("Wrong DB username or password!")
    elif err.errno == connector.errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist!")
    else:
        print(err)
    exit(1)


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print("-----------------------------")
        request_path = self.path

        key = parse_querystring(self, "key")
        print("Authentication key: " + repr(key))

        if not key:
            print("Invalid parameters!")
            send_failure(self, 400)
            return
        else:
            if key[0] not in arduino_keys.values():
                print("Authentication failed!")
                send_failure(self, 401)
                return

        # authenticated successfully
        for key_id, value in arduino_keys.items():
            if key[0] == value:
                name = key_id
                break
        print("Authenticated as " + name + "!")
        send_success(self)

        source = parse_querystring(self, "source")
        print("Data source: " + repr(source))

        value = parse_querystring(self, "value")
        print("Data value: " + repr(value))

        # pass data to mysql server
        if source and value:
            cursor = cnx.cursor()

            data = (name, source[0], value[0], datetime.now())
            cursor.execute(add_metric, data)

            cnx.commit()
            cursor.close()

    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET


def parse_querystring(req_obj, value):
    return parse_qs(urlparse(req_obj.path).query).get(value, [])  # None)


def send_success(req_obj):
    req_obj.send_response(200)
    req_obj.send_header('Content-type', 'text/html')
    req_obj.end_headers()
    req_obj.send_header("Set-Cookie", "success=true")


def send_failure(req_obj, code):
    req_obj.send_response(code)
    req_obj.send_header('Content-type', 'text/html')
    req_obj.end_headers()
    req_obj.send_header("Set-Cookie", "success=true")


def main():
    port = 8080
    print('Listening on localhost:%s' % port)
    # Must specify IP to open connection to external devices
    server = HTTPServer(('192.168.43.244', port), RequestHandler)
    # server = HTTPServer(('', port), RequestHandler)
    # server.socket = wrap_socket(server.socket, server_side=True,
    #                             certfile='certs/mycert.pem')
    server.serve_forever()


if __name__ == "__main__":
    main()
    cnx.close()
