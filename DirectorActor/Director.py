#! /usr/bin/python

import os
import threading
import requests
from cgi import parse_qs
from wsgiref.simple_server import make_server

"""
Python class takes a graph adjacency list and creates the corresponding calvin actor graph dynamically

Inputs :
        Adjacency list of Graph : JSON
        edge_count : integer
        vertex_count : integer
Output :
        A calvin app with new data flow
"""
# script algorithm
#  1. start web server in forever mode
#  2. receive new adjacency list via POST
#  3. check for running apps
#  4. check if current app graph flow is different from original graph
#       4.1 if graphs are same, do nothing, keep looping
#       4.2 if graphs are different
#            4.2.1 create new calvin script
#            4.2.2 redeploy app with new calvin script
#            4.2.3 if redeploy is success keep listening for new configs
#                    4.2.3.1 set old config as new graph
#                    4.2.3.2 kill existing app
#            4.2.4 if redeploy fails, rollback to last config
#   Goto 2


test_graph_old = {"node1": ["node2"],
                  "node2": ["node3"],
                  "node3": ["node4"]
                  }

test_graph_new = {"node1": ["node3"],
                  "node2": ["node4"],
                  "node3": ["node2"]
                  }

test_graph_post = {}

start = "node1"
destination = "node4"

RUNTIME_PORT = 7500
CONTROL_PORT = 7501
REST_PORT = 7800

CONTROL_URI = "http://127.0.0.1:" + CONTROL_PORT

# sample post
# curl -X POST -H "Content-Type: application/json" -d 'graph=
# {"node1": ["node2"], "node2": ["node3"], "node3": ["node4"]}}' http://localhost:1337
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

        return 'From POST: %s' % ''.join('%s: %s' % (k, v) for k, v in test_graph_post.iteritems()) + "\n"
    else:  # GET
        d = parse_qs(environ['QUERY_STRING'])  # turns the qs to a dict
        return 'From GET: %s' % ''.join('%s: %s' % (k, v) for k, v in test_graph_post.iteritems()) + "\n"


def start_web_server():
    httpd = make_server('', REST_PORT, web_server)
    print "HTTP server started on port " + REST_PORT
    httpd.serve_forever()


def read_new_config(test_graph_new, destination):
    # read the calvin file
    with open('application.calvin') as fp, open('application_new.calvin', 'w') as foutp:
        for line in fp:
            if '>' in line and ".result" in line:
                # skip these mappings and add new from actor graph
                continue
            else:
                foutp.write(line)
        for nk in test_graph_new:
            for neighbour in test_graph_new[nk]:
                print (nk, neighbour)
                line = nk + ".result > " + neighbour + ".temp_network\n"
                foutp.write(line)
        # create the destination actor mapping to std out actor
        line = destination + ".result > out.data\n"
        foutp.write(line)


def kill_application():
    # os.system('ls')
    r = requests.get(CONTROL_URI)
    r.json()
    print r
    app_id = r.text
    curr_app_id = app_id.replace('["', '').replace('"]', '')
    app_kill_command = "cscontrol http://127.0.0.1:" + CONTROL_PORT \
                       + " applications delete " + curr_app_id
    kill_code = os.command(app_kill_command)
    if kill_code is 0:
        print "Application: " + curr_app_id + " has been stopped..."
    else:
        print("!! Unable to stop application id: " + curr_app_id)

    return curr_app_id


def roll_back():
    # redeploy with the previous script
    rollback_command = "cscontrol http://127.0.0.1:" + CONTROL_PORT \
                       + " deploy --reqs application.deployjson avgtemp.calvin"
    code = os.system(rollback_command)


def main():
    # start the http server for receiving network config
    threading.Thread(target=start_web_server).start()

    # process the actor graph and destination node from received config
    read_new_config(test_graph_new, destination)
    curr_app_id = kill_application()

    # redeploy app with new actor graph
    dep_app_command = "cscontrol http://127.0.0.1:" + CONTROL_PORT \
                      + " deploy --reqs application_new.deployjson avgtemp.calvin"
    code = os.system(dep_app_command)
    # print app_id
    if code is not 0:
        # roll back to previous config
        roll_back()
    else:
        print("Successfully switched to new configuration...")


if __name__ == "__main__":
    main()
