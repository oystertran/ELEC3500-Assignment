from socket import *
import os
from urllib.parse import *
import time # import module to get last modification time of file
from email.utils import formatdate


# Global variables
proxy_host='localhost'
proxy_port=8888
CACHE_DIR = 'PROXY_CACHE' # Directory for cache files
BUFFER_SIZE = 4096    # Receive buffer

# Create the cache directory if it doesn't already exist
os.makedirs(CACHE_DIR, exist_ok=True)

def start_proxy_server(host, port):
    # Create a server socket
    servSock = socket(AF_INET, SOCK_STREAM)
    # TODO: Start - Bind the socket to a port and begin listening
    servSock.bind((host, port))
    servSock.listen(10)
    # TODO: End

    print('Proxy server running...') # message to know that the socket is listening

    while True:
        cliSock, addr = servSock.accept()
        print('Accepted a connection from:', addr)
        handle_client(cliSock)


def handle_client(cliSock):
    # TODO: Start - Receive the request
    request = cliSock.recv(BUFFER_SIZE).decode('utf-8')
    # TODO: End

    if not request:
        cliSock.close()
        return
    
    #Get the request url
    url = request.split()[1]

    # Remove unnecessary characters from url
    while url.startswith('/') or url.startswith(':'):
        url = url[1:]
    
    # Assign file path in cache
    cacheFilePath = os.path.join(CACHE_DIR, url.replace('/','_').replace(':','_'))

        
    try:
        # TODO: Start - Create socket to fetch content from web
        webSock = socket(AF_INET, SOCK_STREAM)
        # TODO: End

        # TODO: Start - From the url, get the host name and path
        # e.g the hostname is gaia.cs.umass.edu, 
        # the path is /wireshark-labs/HTTP-wireshark-file1.html 
        url = url.split(":/", 1)[1] # take the second half of the url after https://
        urlparts = url.split("/", 1) # split the hostname and path into 2 parts
        webHostn = urlparts[0] # host name is the firt section
        webPath = urlparts[1] # webpath is the second section
        # TODO: End

        # Replace empty path with '/' character
        if webPath == '':
            webPath = '/'
        
        # TODO: Start - Establish connection with web server
        webSock.connect((webHostn, 80))
        # TODO: End 

        # Check whether the file exists in the cache
        if os.path.exists(cacheFilePath):
            print(f"File found in cache: {url}")
            # TODO: Start - Get the last modification time of the file and 
            # construct if-modified-since header to request
            # (Hint: you may need to import another module to help with this)   
            lastModified = os.path.getmtime(cacheFilePath) # get last modification time 
            ifModSince = formatdate(timeval=lastModified, usegmt=True)
            #TODO: End
        else:
            ifModSince="\r\n"

        # Build a simple GET request
        webRequest = "GET " + webPath + " HTTP/1.1\r\nHost: " + webHostn +"\r\n" + ifModSince 

        # TODO: Start - Send the request to the web server
        webSock.sendall(webRequest.encode('utf-8'))
        # TODO: End

        # TODO: Start - Receive response from the web server
        response = b''
        while True:
            data = webSock.recv(BUFFER_SIZE)
            if not data:
                break
            response += data
        # TODO: End

        # TODO: Check for 304 Not Modified status code
        if b"304 Not Modified" in response:
        #TODO: End
            print(f"Not Modified, sending file from cache: {url}")
            # TODO: Start - Read data from the cache and send to client
            with open(cacheFilePath, 'rb') as cache_file:
                cached_data = cache_file.read()
                cliSock.sendall(cached_data)
            # TODO: End
            
        else:
            # Cache the response
            with open(cacheFilePath, 'wb') as cache_file:
                cache_file.write(response)
            
            # TODO: Start - Forward response to the client
            cliSock.sendall(response)
            # TODO: End

    # Handle errors
    except Exception as e:
        # TODO: Start - Print an error message and send HTTP error code to the client
        print("ERROR CODE PRINTED");
        error_response = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html\r\n"
            "Content-Length: 44\r\n"
            "\r\n"
            "<html><body><h1>404 Not Found</h1></body></html>"
        )
        # Send the error response to the client through the socket
        cliSock.sendall(error_response.encode('utf-8'))
        # TODO: End

    # TODO: Start - Close the client socket 
    cliSock.close()
    webSock.close()
    # TODO: End

    return

if __name__ == "__main__":
    start_proxy_server(proxy_host, proxy_port)

