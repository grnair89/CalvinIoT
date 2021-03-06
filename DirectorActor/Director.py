# script algorithm
#  1. start web server in forever mode
#  2. receive new adjacency list via POST
#  3. check for running apps
#  4. check if current app graph flow is different from original graph
#       4.1 if graphs are isomorphic, do nothing, keep looping
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
        self.actor_graph_current = {"node1": ["node2"],
                                    "node2": ["node3"],
                                    "node3": ["node4"]
                                    }

        self.actor_graph_new = {"node1": ["node3"],
                                "node3": ["node4"]
                                }
        self.start = "node1"
        self.destination = "node4"

        self.RUNTIME_PORT = 6500
        self.CONTROL_PORT = 6501
        self.REST_PORT = 7505
        self.CONTROL_URI = "http://127.0.0.1:"+str(self.CONTROL_PORT)+"/applications"

        self.G = nx.DiGraph()
        self.G.add_edges_from([('node1', 'node2'), ('node2', 'node3'), ('node3', 'node4')], weight=1)

        self.H = nx.DiGraph()
        # self.H.add_edges_from([('node1', 'node3'), ('node3', 'node4')], weight=1)

        # sample post
        # curl -X POST -H "Content-Type: application/json" -d 'graph={"node1": ["node2"], "node2": ["node3"], "node3": ["node4"]}}' http://localhost:9450
        self.test_graph_post = {}

    def web_server(self, environ, start_response):
        status = '200 OK'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        if environ['REQUEST_METHOD'] == 'POST':
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            # global test_graph_post
            # global actor_graph_current
            self.actor_graph_new = self.test_graph_post
            self.test_graph_post = parse_qs(request_body)

            return 'From POST: %s' % ''.join('%s: %s' % (k, v) for k, v in test_graph_post.iteritems()) + "\n"
        else:  # GET
            d = parse_qs(environ['QUERY_STRING'])  # turns the qs to a dict
            return 'From GET: %s' % ''.join('%s: %s' % (k, v) for k, v in test_graph_post.iteritems()) + "\n"

    def start_web_server(self):
        httpd = make_server('', self.REST_PORT, self.web_server)
        print "HTTP server started on port " + str(self.REST_PORT)
        httpd.serve_forever()

    def read_new_config(self, actor_graph_new, destination):
        # read the calvin file
        with open('avgapp.calvin') as fp, open('avgapp_output.calvin', 'w') as foutp:
            for line in fp:
                if ('>' in line and ".result" in line) or ('node2' in line) or ('sensor2' in line) or ('rand2' in line):
                    # skip these mappings and add new from actor graph
                    continue
                else:
                    foutp.write(line)
            for vertex in actor_graph_new:
                for neighbour in actor_graph_new[vertex]:
                    print (vertex, neighbour)
                    line = vertex + ".result > " + neighbour + ".temp_network\n"
                    foutp.write(line)
            # create the destination actor mapping to std out actor
            line = destination + ".result > out.data\n"
            foutp.write(line)

    def kill_application(self):
        # os.system('ls')
        r = requests.get(self.CONTROL_URI)
        # r.json()
        # print r.content
        app_id = r.text
        curr_app_id = app_id.replace('["', '').replace('"]', '')

        curr_app_id = curr_app_id.strip()

        print "curr_app_id: "+str(curr_app_id)
        app_kill_command = "cscontrol http://127.0.0.1:" + str(self.CONTROL_PORT) \
                           + " applications delete " + str(curr_app_id)

        kill_code = os.system(app_kill_command)
        print "\napp_kill_command: "+app_kill_command
        print "\nkill_code : "+str(kill_code)
        if kill_code is 0:
            print "Application: " + curr_app_id + " has been stopped..."
        else:
            print("!! Unable to stop application id: " + curr_app_id)

        return curr_app_id

    def roll_back(self):
        # redeploy with the previous script
        rollback_command_distributed = "cscontrol http://127.0.0.1:" + str(self.CONTROL_PORT) \
                           + " deploy --reqs application.deployjson avgapp.calvin"

        rollback_command = "cscontrol http://127.0.0.1:" + str(self.CONTROL_PORT) \
                           + " deploy avgapp.calvin"

        print "rollback_command : " + str(rollback_command)
        code = os.system(rollback_command)
        if code is 0:
            print "Rolled back to previous configuration..."
        else:
            print "Error during rollback!!"

    def perform_config_check(self):
        print "Performing config check ...\n"
        result = self.is_isomorphic(self.G, self.H)
        if not result:
            print "Deploying received actor graph...\n"
            print self.test_graph_post
            self.deploy_new_actor_graph()
        else:
            print "No changes in actor graph...\n"
            print "\nCurrently deployed Actor Graph: "
            print self.actor_graph_current
            print "\nReceived Actor Graph: "
            print self.test_graph_post

    def start_config_check_new(self):

        while True:
            H_edge_list = []
            time.sleep(5)
            print "\nNewly Received graph : "
            print self.test_graph_post

            print "\nCurrent graph"
            print self.actor_graph_current

            for key in self.test_graph_post.keys():
                # test_graph_string = test_graph_post[i]
                # test_graph_string.replace('["', '').replace('"]', '')
                # print test_graph_post[i]
                test_graph = self.test_graph_post[key]

                for key in test_graph:

                    first = key[1:len(key) - 2]
                    # print first
                    first = first.replace("{", "").replace("}", "").replace("\"", "").replace(" ", "").replace("[", "").replace("]", "")
                    # print first

                    second = first.split(",")

                    for item in second:
                        itemList = item.split(":")
                        # print("\n"+itemList[0]+"-->"+itemList[1])

                        edge = (itemList[0], itemList[1])

                        # print edge

                        H_edge_list.append(edge)

            if H_edge_list:
                self.H.clear()
                self.H.add_edges_from(H_edge_list, None, weight=1)
                self.perform_config_check()

            print "\nReceived actor graph : "
            print self.H.edges()

            print "\nCurrent actor graph : "
            print self.G.edges()

    def is_isomorphic(self, g1, g2):
        return iso.is_isomorphic(g1, g2)  # no weights considered

    def deploy_new_actor_graph(self):
        # process the actor graph and destination node from received config

        adj_list = nx.to_dict_of_lists(self.H, nodelist=None)
        self.read_new_config(adj_list, self.destination)

        # get the app hash and kill it
        curr_app_id = self.kill_application()

        # redeploy app with new actor graph
        dep_app_command_distributed = "cscontrol http://127.0.0.1:" + str(self.CONTROL_PORT) \
                          + " deploy --reqs application_new.deployjson avgapp_output.calvin"

        dep_app_command = "cscontrol http://127.0.0.1:" + str(self.CONTROL_PORT) \
                                      + " deploy avgapp_output.calvin"

        print "dep_app_command : " + str(dep_app_command)
        code = os.system(dep_app_command)
        # print app_id
        if code is not 0:
            # roll back to previous config
            self.roll_back()
        else:
            print("Successfully switched to new configuration...")
            # Update current to newly deployed actor graph
            self.G = self.H
            self.actor_graph_current = adj_list

if __name__ == "__main__":
    test_graph_post = {}

    D = Director()

    # start the http server for receiving network config
    threading.Thread(target=D.start_web_server).start()

    # start the config checker
    D.start_config_check_new()
