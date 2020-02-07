#!/usr/bin/env python3
# coding: utf-8
# Copyright 2020 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Justin Liew
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        if len(data) > 0:
            return int(data.split()[1])
        else:
            return 500

    def get_headers(self,data):
        response = data.split('\r\n\r\n')
        return response[0]

    def get_body(self, data):
        response = data.split('\r\n\r\n')
        return '\r\n\r\n'.join(response[1:])
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        try:
            return buffer.decode('utf-8')
        except UnicodeDecodeError:
            return buffer.decode('unicode-escape')
        
        
    def GET(self, url, args=None):
        # prefix with http:// if missing
        if url[0:4].lower() != 'http':
            url = 'http://' + url
        
        # parse url
        parsedUrl = urllib.parse.urlsplit(url)
        requestPath = parsedUrl.path
        if parsedUrl.query:
            #q = urllib.parse.parse_qsl(parsedUrl.query, True)
            #encodedQuery = urllib.parse.urlencode(q)
            #requestPath += '?' + encodedQuery 
            requestPath += '?' + parsedUrl.query
        if requestPath == '':
            requestPath = '/'
        requestHost = parsedUrl.netloc

        # generate GET request headers
        get = "GET " + requestPath + " HTTP/1.1\r\n"
        host = "Host: " + requestHost + "\r\n"
        accept = "Accept: */*\r\n"
        connection = "Connection: close\r\n"
        headerEnd = "\r\n"
        request = get + host + accept + connection + headerEnd

        # connect to host
        self.connect(parsedUrl.hostname, parsedUrl.port if parsedUrl.port else 80)

        # send GET request
        self.sendall(request)

        # store response
        response = self.recvall(self.socket)

        code = self.get_code(response)
        body = self.get_body(response)
        
        # for user, print result to stdout
        #print(body, end = '')
        
        # for developer, return result as HTTPResponse object
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # prefix with http:// if missing
        if url[0:4].lower() != 'http':
            url = 'http://' + url

        # parse
        argString = ""
        if args:
            argString = urllib.parse.urlencode(args)
        
        # parse url
        parsedUrl = urllib.parse.urlsplit(url)
        requestPath = parsedUrl.path
        if parsedUrl.query:
            requestPath += '?' + parsedUrl.query
        if requestPath == '':
            requestPath = '/'
        requestHost = parsedUrl.netloc

        # generate POST request headers
        post = "POST " + requestPath + " HTTP/1.1\r\n"
        host = "Host: " + requestHost + "\r\n"
        accept = "Accept: */*\r\n"
        connection = "Connection: close\r\n"
        contentType = "Content-Type: application/x-www-form-urlencoded\r\n"
        contentLength = "Content-Length: 0\r\n"
        if args:
            contentLength = "Content-Length: " + str(len(bytes(argString, 'utf-8'))) + "\r\n" 
        headerEnd = "\r\n"
        request = post + host + accept + connection + contentType + contentLength + headerEnd + argString

        # connect and send request
        self.connect(parsedUrl.hostname, parsedUrl.port if parsedUrl.port else 80)
        self.sendall(request)

        # receive and store response, extract status code and body
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)

        # for user, print result to stdout
        #print(body, end = '')

        # for developer, return result as HTTPResponse object
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ).body, end='')
    else:
        print(client.command( sys.argv[1] ).body, end='')
    
