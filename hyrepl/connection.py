import socket
import threading
import socketserver
import uuid
from nrepl.bencode import encode, decode 
from hyrepl.errors import NREPLError
from hyrepl.repl import Repl
from queue import Queue
import time
import http.server
import sys
import random

operations = {}
required_map = {}


class HyreplSTDIN(Queue):
    """This is hack to override sys.stdin."""
    def __init__(self):
        super().__init__()
        self.self = None
        self.sess = None
        self.msg = None

    def readline(self):
        """Hackin'"""
        # We get the self from the instance of the thread so we can keep state.
        a = threading.Thread(target=self.self.send_request, args=(self.self, self.sess))
        a.start()

        #just add something so the queue think we work.
        self.put(1)
        self.join()

        return self.msg

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """The actuall thread we launch on ever request"""
    allow_reuse_address = True

    sessions = {} 


    sys.stdin = HyreplSTDIN()

    def send(self):
        for i in self.outs:
            ret = encode(i)
            self.request.sendall(bytes(ret, 'utf-8'))
            if i.get("status"):
                if "done" in i["status"]:
                    del self.sessions[i["session"]]
        self.outs = []

    def send_request(self2, self, sess):
        ret = encode({"status": ["need-input"], "session": sess})
        self.request.sendall(bytes(ret, 'utf-8'))

    def handle(self):
        self.outs = []

        ret = {"status": []}

        in_data = str(self.request.recv(1024), 'utf-8')

        dec_dat = decode(in_data)
        decoded_data = [i for i in dec_dat][0]
        
        if "session" not in decoded_data:
            sess = str(uuid.uuid4()) 
            self.sessions[sess] = None
        else:
            if decoded_data["session"] not in list(self.sessions.keys()):
                print("Add errors")

        ret["session"] = sess

        sys.stdin.self = self
        sys.stdin.sess = sess

        if decoded_data["op"] in operations:
            op = decoded_data["op"]
            self.sessions[sess] = operations[op](self, sess, decoded_data)


        if self.sessions[sess] == None:
            return 0
        elif isinstance(self.sessions[sess],dict):
            ret.update(self.sessions[sess])

        ret["status"].append("done")
        self.outs.append(ret)
        self.send()
        return 0


    def operation(operation_val):
        def _(fn):
            operations[operation_val] = fn
        return _

    def required_params(*args):
        def _(fn):
            def check(self, sess, expr):
                for i in args:
                    if i not in list(expr.keys()):
                        # If we are missing a required param in the map
                        # Gief better handling
                        raise
                return fn(self, sess, expr)
            return check
        return _

    @operation("eval")
    @required_params("code")
    def eval_operation(self, session, msg):
        repl = Repl()
        ret = repl.eval(msg["code"])
        for i in ret:
            m = {"session": session}
            m.update(i)
            self.outs.append(m)
        return True
        

    @operation("clone")
    def clone_operation(self, session, msg):
        sess = str(uuid.uuid4())
        return {"new-session": sess}

    @operation("close")
    @required_params("session")
    def close_operation(self, session, msg):
        del self.sessions
        return True

    @operation("describe")
    def describe_operation(self, session, msg):
        return None

    @operation("interrupt")
    @required_params("session")
    def interrupt_operation(self, session, msg):
        return None

    @operation("load-file")
    @required_params("file")
    def load_file_operation(self, session, msg):
        pass

    @operation("ls-sessions")
    def ls_sessions_opeartion(self, session, msg):
        self.outs.append({"sessions": list(self.sessions.keys())})
        return True

    @operation("stdin")
    def stdin_operation(self, session, msg):
        sys.stdin.msg = msg["value"]
        # Because sys.stdin is in reality a queue, we can do magic!
        sys.stdin.task_done()
        return None



class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Threaded server"""
    daemon_threads = True
    allow_reuse_address = True


class nREPLServerHandler(object):
    """Server abstraction"""

    def __init__(self, host, port):
        while True:
            try:
                self.server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
            except:
                pass
            else:
                print("Started")
                break
        self.ip, self.port = self.server.server_address

    def start(self):
        """Starts the server"""
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self):
        """Stops the server"""
        del self.server_thread
        self.server.shutdown()