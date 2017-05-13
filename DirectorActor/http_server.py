from cgi import parse_qs
from wsgiref.simple_server import make_server
import threading
import time
import networkx as nx
import networkx.algorithms.isomorphism as iso

test_graph_post = {}

test_graph_current = {}

G = nx.DiGraph()
G.add_edges_from([('node1', 'node3'), ('node3', 'node4')], weight=1)

H = nx.DiGraph()


def web_server(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'application/json')]
    start_response(status, headers)
    if environ['REQUEST_METHOD'] == 'POST':
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(request_body_size)
        global test_graph_post
        global test_graph_current
        test_graph_current = test_graph_post
        test_graph_post = parse_qs(request_body)

        return 'From POST: %s' % ''.join('%s: %s' % (k, v) for k, v in test_graph_post.iteritems())+"\n"
    else:  # GET
        d = parse_qs(environ['QUERY_STRING'])  # turns the qs to a dict
        return 'From GET: %s' % ''.join('%s: %s' % (k, v) for k, v in test_graph_post.iteritems())+"\n"


def start_web_server():
    httpd = make_server('', 9505, web_server)
    print "Serving on port 9505..."
    httpd.serve_forever()


def check():

    while True:
        H_edge_list = []
        time.sleep(5)
        print "Newly Received graph : "
        print test_graph_post

        print "\nCurrent graph"
        print test_graph_current

        for key in test_graph_post.keys():
            # test_graph_string = test_graph_post[i]
            # test_graph_string.replace('["', '').replace('"]', '')
            # print test_graph_post[i]
            test_graph = test_graph_post[key]

            for key in test_graph:

                first = key[1:len(key)-2]
                #print first
                first = first.replace("{", "").replace("}", "").replace("\"", "").replace(" ", "").replace("[", "").replace("]", "")
                #print first

                second = first.split(",")

                for item in second:
                    itemList = item.split(":")
                    #print("\n"+itemList[0]+"-->"+itemList[1])

                    edge = (itemList[0], itemList[1])

                    #print edge

                    H_edge_list.append(edge)

        if H_edge_list:

            global G
            if iso.is_isomorphic(G, H):
                G = H
            H.clear()
            H.add_edges_from(H_edge_list, None, weight=1)

        print "\nReceived graph : "
        print H.edges()

        # print "\nCurrent graph : "
        # print G.edges()

        hello = nx.to_dict_of_lists(H, nodelist=None)
        print "Converted H obj to Dictionary of Lists"
        print hello


def main():
    threading.Thread(target=start_web_server).start()
    check()

main()




