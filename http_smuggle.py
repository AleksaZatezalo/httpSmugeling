#!/usr/bin/env python3

import socket
import time
import argparse
from urllib.parse import urlparse

def test_header_parsing(host, port=80):
    """
    Tests server behavior with different header combinations 
    and analyzes response patterns
    """
    # Test cases to analyze server parsing behavior
    test_cases = [
        {
            "name": "Both Headers",
            "request": (
                f"POST / HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                "Content-Length: 5\r\n" 
                "Transfer-Encoding: chunked\r\n"
                "Connection: keep-alive\r\n\r\n"
                "0\r\n\r\n"
            )
        },
        {
            "name": "TE Only",
            "request": (
                f"POST / HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                "Transfer-Encoding: chunked\r\n"
                "Connection: keep-alive\r\n\r\n"
                "0\r\n\r\n"
            )
        }
    ]
    
    results = []
    
    for test in test_cases:
        try:
            # Create new connection for each test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            
            # Send request and measure timing
            start_time = time.time()
            sock.send(test["request"].encode())
            
            # Get response and analyze headers
            response = sock.recv(4096).decode('utf-8', errors='ignore')
            response_time = time.time() - start_time
            
            # Parse response headers
            headers = {}
            for line in response.split('\r\n'):
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    headers[key.lower()] = value
            
            results.append({
                "test_name": test["name"],
                "response_time": response_time,
                "connection": headers.get('connection', 'Not specified'),
                "content_length": headers.get('content-length', 'Not specified'),
            })
            
        except Exception as e:
            print(f"Error during {test['name']}: {str(e)}")
        finally:
            sock.close()
            time.sleep(1)  # Prevent overwhelming the server
    
    return analyze_results(results)

def analyze_results(results):
    """
    Analyzes test results for potential parsing inconsistencies
    """
    for r in results:
        print(f"\nTest: {r['test_name']}")
        print(f"Response time: {r['response_time']:.2f}s")
        print(f"Connection header: {r['connection']}")
        print(f"Content-Length header: {r['content_length']}")
    
    # Check for inconsistent connection header behavior
    both_headers = next(r for r in results if r["test_name"] == "Both Headers")
    te_only = next(r for r in results if r["test_name"] == "TE Only")
    
    if both_headers["connection"].lower() == "close" and \
       te_only["connection"].lower() == "keep-alive":
        print("\n[!] Potential header parsing inconsistency detected:")
        print("- Server returns 'Connection: close' with both headers")
        print("- Server returns 'Connection: keep-alive' with TE only")
        print("- Response timing differs by: " 
              f"{abs(both_headers['response_time'] - te_only['response_time']):.2f}s")
    
def main():
    parser = argparse.ArgumentParser(description='Test HTTP header parsing behavior')
    parser.add_argument('url', help='Target URL (e.g., example.com)')
    args = parser.parse_args()
    
    parsed_url = urlparse(args.url if '://' in args.url else f'http://{args.url}')
    host = parsed_url.hostname
    port = parsed_url.port or 80
    
    print(f"Testing {host}:{port} for header parsing behavior...")
    test_header_parsing(host, port)

if __name__ == "__main__":
    main()
