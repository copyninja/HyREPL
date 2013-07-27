#!/usr/bin/env python
import os, unittest, subprocess, re, signal, time
import socket
import nrepl
import threading
from nrepl.bencode import encode, decode
from hyrepl.connection import nREPLServerHandler
import time
import queue
import sys


PY2 = sys.version_info[0] == 2
if not PY2:
    port_type = bytes
else:
    port_type = ()


ip = "127.0.0.1"
port = 9999


p = nREPLServerHandler(ip,port)
th = threading.Thread(target=p.start)
th.start()

def soc_send(message):
    reply = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reply.connect((ip, port))
    msg = bytes(encode(message), 'utf-8')
    ret = []
    reply.sendall(msg)
    while True:
        response = str(reply.recv(2048), 'utf-8')
        if response:
            [ret.append(l) for l in decode(response)]
        if "done" in response:
            break
    reply.close()
    return ret


def test_code_eval():
    code = {"op": "eval", "code": "(+ 2 2)"}
    ret = soc_send(code)
    print(ret)
    assert len(ret) == 2
    value, status = ret
    assert value["value"] == '4'
    assert "done" in status["status"]
    assert value["session"] == status["session"]


def test_stdout_eval():
    code = {"op": "eval", "code": '(print "Hello World")'}
    ret = soc_send(code)
    print(ret)
    assert len(ret) == 3
    value, out, status = ret
    assert value["value"] == 'None'
    assert out["out"] == "Hello World\n"
    assert "done" in status["status"]
    assert value["session"] == out["session"] == status["session"]



def stdin_send(code, my_queue):
    ret = soc_send(code)
    print(ret)
    my_queue.put(ret)


def test_stdin_eval():

    """The current implementation will send all the responses back 
    into the first thread which dispatched the (def...), so we throw 
    it into a thread and add a Queue to get it.
    Bad hack. But it works."""

    my_queue = queue.Queue()


    code = {"op": "eval", "code": '(def a (input))'}
    t = threading.Thread(target=stdin_send, args=(code,my_queue))
    t.start()

    time.sleep(1)
    reply = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reply.connect((ip, port))
    code = {"op": "stdin", "value": "test"}
    reply.sendall(bytes(encode(code), 'utf-8'))
    t.join()
    ret = my_queue.get()
    
    assert len(ret) == 3
    input_request, value, status = ret
    assert value["value"] == 'test'
    assert input_request["status"] == ["need-input"]
    assert "done" in status["status"]
    assert value["session"] == input_request["session"] == status["session"]



def test_exit():
    global th
    del th
    p.stop()

