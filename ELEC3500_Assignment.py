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
    request = cliSock.recv(BUFFER_SIZE).decode('utf-8') #The request is sent in utf-8 format so we decode it 
    print ("Request Received") #Print to know we have received the request
    # TODO: End

    if not request:
        cliSock.close()
        return
    
    #Get the request url
    url = request.split()[1]
    print("url is: "+url)
    

    # Remove unnecessary characters from url
    while url.startswith('/') or url.startswith(':'):
        url = url[1:]
        
    
    # Assign file path in cache
    cacheFilePath = os.path.join(CACHE_DIR, url.replace('/','_').replace(':','_'))
    print("cacheFilePath is: " + cacheFilePath)
    try:
        # TODO: Start - Create socket to fetch content from web
        webSock = socket(AF_INET, SOCK_STREAM)
        print("Web Socket Created")
        # TODO: End

        # TODO: Start - From the url, get the host name and path
        # e.g the hostname is gaia.cs.umass.edu, 
        # the path is /wireshark-labs/HTTP-wireshark-file1.html
        #Call helper function to get extract the host name and path from the url
        webHostn = get_hostname(url)
        print("web host is: " + webHostn)
        webPath = get_path(url)
        print("web path is: " + webPath)
        # TODO: End

        # Replace empty path with '/' character
        if webPath == '':
            webPath = '/'
        
        # TODO: Start - Establish connection with web server
        webSock.connect((webHostn, 80))
        print("Connection established")
        # TODO: End 

        # Check whether the file exists in the cache
        if os.path.exists(cacheFilePath):
            print(f"File found in cache: {url}")
            # TODO: Start - Get the last modification time of the file and 
            # construct if-modified-since header to request
            # (Hint: you may need to import another module to help with this)   
            lastModified = os.path.getmtime(cacheFilePath) # get last modification time 
            print("lastModified: " + str(lastModified))
            ifModSince = formatdate(timeval=lastModified, usegmt=True)
            print("ifModSince: " + str(ifModSince))
            #TODO: End
        else:
            ifModSince="\r\n"

        # Build a simple GET request
        webRequest = f"GET {webPath} HTTP/1.1\r\nHost: {webHostn}\r\nIf-Modified-Since: {ifModSince}\r\n\r\n"
        print("webRequest: " + webRequest)
        # TODO: Start - Send the request to the web server
        webSock.sendall(webRequest.encode('utf-8'))
        # TODO: End

        # TODO: Start - Receive response from the web server
        response = b'' #Response is in byte form 
        while True:
            data = webSock.recv(BUFFER_SIZE)
            if not data:
                break
            response += data
        print("Response: " + response.decode('utf-8'))
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
        print(e)
        
        # Get the exception message as the error response body
        error_message = f"<h1>Exception Occurred: {str(e)}</h1>"
        error_code = response.split(b'\r\n')[0].decode('utf-8') #extract the error code from the web response
        # Build the full HTTP response
        error_response = (
            f"HTTP/1.1 {error_code} \r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(error_message)}\r\n"
            "\r\n"
            f"<html><body>{error_message}</body></html>"
        )

        # Send the error response to the client through the socket
        cliSock.sendall(error_response.encode('utf-8'))
        # TODO: End 

    # TODO: Start - Close the client socket 
    cliSock.close()
    webSock.close()
    # TODO: End

    return

# This is a helper function to extract the URL from the request
def get_url (request):
    request_part = request.splitlines()

    for part in request_part:
        if part.startswith("Referer:"):
            referer_url = part.split(":", 1)[1].strip()
            return referer_url
    return None

# Helper function that extract the host name from the url
# Precondition: a url in the form of string existed
# Postcondition: return the host name from the url
def get_hostname(url):
    # Remove leading slashes if present
    url = url.lstrip('/')
    
    # Split by the first slash to separate hostname from the path
    hostname = url.split('/', 1)[0]
    
    return hostname

# Helper function that extract the path from the url
# Precondition: a url in the form of string existed
# Postcondition: return the path from the url
def get_path(url):
    # Remove leading slashes if present
    url = url.lstrip('/')
    
    # Split by the first slash and extract the part after the hostname
    parts = url.split('/', 1)
    
    # If there's a path after the hostname, return it; otherwise, return "/"
    if len(parts) > 1:
        return '/' + parts[1]
    else:
        return '/'


if __name__ == "__main__":
    start_proxy_server(proxy_host, proxy_port)

