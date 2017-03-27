from cgi import parse_qs
from wsgiref.simple_server import make_server
import threading
import time


test_graph_post = {}

def web_server(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'application/json')]
    start_response(status, headers)
    if environ['REQUEST_METHOD'] == 'POST':
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(request_body_size)
        global test_graph_post
        test_graph_post = parse_qs(request_body)

        return 'From POST: %s' % ''.join('%s: %s' % (k, v) for k, v in test_graph_post.iteritems())+"\n"
    else:  # GET
        d = parse_qs(environ['QUERY_STRING'])  # turns the qs to a dict
        return 'From GET: %s' % ''.join('%s: %s' % (k, v) for k, v in test_graph_post.iteritems())+"\n"


def start_web_server():
    httpd = make_server('', 7700, web_server)
    print "Serving on port 7700..."
    httpd.serve_forever()


def check():
    while True:
        time.sleep(5)
        print "Inside the first infinite loop ...\n"
        print "New graph : "
        print test_graph_post

def main():
    threading.Thread(target=start_web_server).start()
    check()

main()




