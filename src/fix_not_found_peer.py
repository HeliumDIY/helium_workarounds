#!/usr/bin/python3

import re
import requests
import subprocess
import time
import sys
import docker
import os

#method = 'dockercli'
method = 'dockerapi'

def follow(file, sleep_sec=0.1):
    """ Yield each line from a file as they are written.
    `sleep_sec` is the time to sleep after empty reads. """
    line = ''
    while True:
        tmp = file.readline()
        if tmp is not None:
            line += tmp
            if line.endswith("\n"):
                yield line
                line = ''
            elif sleep_sec:
                time.sleep(sleep_sec)
        elif sleep_sec:
            time.sleep(sleep_sec)

if __name__ == '__main__':
    json_msg = {
        "jsonrpc":"2.0",
        "id":"id",
        "method":"peer_refresh",
        "params": {
            "Addr":None
        }
    }
    log_file = os.getenv("LOG_FILE")
    if not log_file:
        log_file = sys.argv[1]
    with open(log_file, 'r') as file:
        print("Tailing file: %s" % (log_file,))
        file.seek(0, 2)
        for line in follow(file):
            m = re.match(r'.*failed to dial (?:challenger|proxy server) "(.*)":? not_found', line)
            print(line, end='')
            if m is not None:
                peer = m.group(1)

                if method == 'jsonrpc':
                    json_msg['params']['Addr'] = peer
                    print("Issuing request to miner to reload peer %s" % (peer,))
                    result = requests.post("http://localhost:4467", json=json_msg)
                    if result.status_code == 200:
                        print("Success")
                    else:
                        print("Error: (%d) %s" % (result.status_code, result.content))
                elif method == 'dockercli':
                    cmd = 'docker exec miner miner peer refresh %s' % (peer,)
                    print("Running: %s" % (cmd,))
                    split_cmd = cmd.split(' ')
                    result = subprocess.check_output(split_cmd)
                    print("Got: %s" % (result,))
                elif method == 'dockerapi':
                    client = docker.from_env()
                    miner_container = client.containers.get("miner")
                    result = miner_container.exec_run("miner peer refresh %s" % (peer,))
                    print(result)
