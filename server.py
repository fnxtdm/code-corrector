import os
import sys
import ssl
from http.server import HTTPServer, SimpleHTTPRequestHandler
from django.core.management import get_commands
from django.core.management import execute_from_command_line
from django.core.handlers.wsgi import WSGIHandler

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Create an SSL context
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile='settings/cert.pem', keyfile='settings/key.pem')


# Create a WSGI server with SSL
class SecureWSGIServer(HTTPServer):
    def get_request(self):
        socket, addr = super().get_request()
        return ssl_context.wrap_socket(socket, server_side=True), addr


if __name__ == '__main__':
    # Run the Django application as a WSGI app
    port = 8000
    try:
        # Initialize the WSGI application
        wsgi_app = WSGIHandler()

        # Start the secure server
        server = SecureWSGIServer(('127.0.0.1', port), SimpleHTTPRequestHandler)
        print(f"Starting secure server on https://127.0.0.1:{port}/")

        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.server_close()