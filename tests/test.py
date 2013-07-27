#!/usr/bin/env python
import os, unittest, subprocess, re, signal, time
import socket
import nrepl
import threading
from nrepl.bencode import encode, decode
from hyrepl.connection import nREPLServerHandler
import time

import sys
PY2 = sys.version_info[0] == 2
if not PY2:
    port_type = bytes
else:
    port_type = ()


ip = "127.0.0.1"
port = 9999


def run_cmd():
    p = subprocess.Popen("python bin/hyrepl",
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True)
    stdout = ""
    stderr = ""
    # Read stdout and stderr otherwise if the PIPE buffer is full, we might
    # wait for ever…
    while p.poll() is None:
        stdout += str(p.stdout.read())
        stderr += str(p.stderr.read())
    return p.returncode, stdout, stderr



def test_cmd():
    args = run_cmd()
    print(args)


def soc_send(message):
    reply = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reply.connect((ip, port))
    msg = bytes(encode(message), 'utf-8')
    ret = []
    reply.sendall(msg)
    while True:
        response = str(reply.recv(2048), 'utf-8')
        if response:
            l = [i for i in decode(response)]
            ret.append(l[0])
        if "done" in response:
            break

def test_code_eval():
    code = {"op": "eval", "code": "(+ 2 2)"}
    ret = soc_send(code)
    assert len(ret) == 2
    value, status = ret
    assert value["value"] == '4'
    assert "done" in status["status"] 

