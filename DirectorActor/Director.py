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


import os
import threading
import requests
import time
from cgi import parse_qs
from wsgiref.simple_server import make_server
import networkx as nx
import networkx.algorithms.isomorphism as iso


class Director(object):
    """
    Python class takes a graph adjacency list and creates the corresponding calvin actor graph dynamically

    Inputs :
            Adjacency list of DiGraph : JSON
            edge_count : integer
            vertex_count : integer
    Output :
            A calvin app with new data flow
    """

    def __init__(self):
        self.test_graph_curr = {"node1": ["node2"],
                                "node2": ["node3"],
                                "node3": ["node4"]
                                }

        self.test_graph_new = {"node1": ["node3"],
                               "node2": ["node4"],
                               "node3": ["node2"]
                               }
        self.start = "node1"
        self.destination = "node4"

        self.RUNTIME_PORT = 7500
        self.CONTROL_PORT = 7501
        self.REST_PORT = 7901
        self.CONTROL_URI = "http://127.0.0.1:" + str(self.CONTROL_PORT)

        self.G = nx.DiGraph()
        self.G.add_edges_from([('A', 'B'), ('B', 'C'), ('B', 'D'), ('D', 'C')], weight=1)

        self.H = nx.DiGraph()
        self.H.add_edges_from([('A', 'B'), ('B', 'C'), ('B', 'D'), ('D', 'C')], weight=1)

        # sample post
        # curl -X POST -H "Content-Type: application/json" -d 'graph={"node1": ["node2"], "node2": ["node3"], "node3": ["node4"]}}' http://localhost:1337
        self.test_graph_post = {}

    def web_server(self, environ, start_response):
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

    def start_web_server(self):
        httpd = make_server('', self.REST_PORT, self.web_server)
        print "HTTP server started on port " + str(self.REST_PORT)
        httpd.serve_forever()

    def read_new_config(self, test_graph_new, destination):
        # read the calvin file
        with open('avgTempAppTest.calvin') as fp, open('avgTempAppTest_output.calvin', 'w') as foutp:
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

    def kill_application(self):
        # os.system('ls')
        r = requests.get(self.CONTROL_URI)
        r.json()
        print r
        app_id = r.text
        curr_app_id = app_id.replace('["', '').replace('"]', '')
        app_kill_command = "cscontrol http://127.0.0.1:" + self.CONTROL_PORT \
                           + " applications delete " + curr_app_id
        kill_code = os.command(app_kill_command)
        if kill_code is 0:
            print "Application: " + curr_app_id + " has been stopped..."
        else:
            print("!! Unable to stop application id: " + curr_app_id)

        return curr_app_id

    def roll_back(self):
        # redeploy with the previous script
        rollback_command = "cscontrol http://127.0.0.1:" + self.CONTROL_PORT \
                           + " deploy --reqs application.deployjson avgtemp.calvin"
        code = os.system(rollback_command)
        if code is 0:
            print "Rolled back to previous configuration..."
        else:
            print "Error during rollback!!"

    def start_config_check(self):
        while True:
            time.sleep(5)
            print "Performing config check ...\n"
            result = self.is_isomorphic(self.G, self.H)
            if not result:
                print "Deploying received actor graph...\n"
                print test_graph_post
                self.deploy_new_actor_graph()
            else:
                print "No changes in actor graph...\n"
                print "Current Graph: "
                print self.test_graph_curr
                print "Received Graph: "
                print test_graph_post

    def is_isomorphic(self, g1, g2):
        return iso.is_isomorphic(g1, g2)  # no weights considered


    def deploy_new_actor_graph(self):
        # process the actor graph and destination node from received config
        self.read_new_config(self.test_graph_new, self.destination)
        curr_app_id = self.kill_application()

        # redeploy app with new actor graph
        dep_app_command = "cscontrol http://127.0.0.1:" + self.CONTROL_PORT \
                          + " deploy --reqs application_new.deployjson avgtemp.calvin"
        code = os.system(dep_app_command)
        # print app_id
        if code is not 0:
            # roll back to previous config
            self.roll_back()
        else:
            print("Successfully switched to new configuration...")


if __name__ == "__main__":

    test_graph_post = {}

    D = Director()

    # start the http server for receiving network config
    threading.Thread(target=D.start_web_server).start()

    # start the config checker
    D.start_config_check()