#!/usr/bin/env python
# Reflects the requests from HTTP methods GET, POST, PUT, and DELETE
# Written by Nathan Hamiel (2010)

from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from ssl import wrap_socket
from mysql import connector


arduino_keys = {'1': "846HqXQ2xPD8TiMjTnshj0UETmxSpT",
                '2': "RadQXmgCJWHbV6YSnuEhObDN1XrYiL",
                '3': "t7XodejIrK35NQSdklCIjM7fyeKIx2"}
db_user = "arduino"
db_pass = "password"


try:
    cnx = connector.connect(user='arduino', password='password',
                            host='127.0.0.1', database='iotsec')
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
        print("Authenticated!")
        send_success(self)

        source = parse_querystring(self, "source")
        print("Data source: " + repr(source))

        value = parse_querystring(self, "value")
        print("Data value: " + repr(value))

        # pass data to mysql server
        if source and value:
            pass

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
    server = HTTPServer(('', port), RequestHandler)
    server.socket = wrap_socket(server.socket, server_side=True,
                                certfile='certs/mycert.pem')
    server.serve_forever()


if __name__ == "__main__":
    main()
