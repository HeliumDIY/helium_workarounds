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

def follow(filename, sleep_sec=0.1, seek_end=True):
    """ Yield each line from a file as they are written.
    `sleep_sec` is the time to sleep after empty reads. """
    file = open(filename, 'r')
    curino = os.fstat(file.fileno()).st_ino
    if seek_end:
        file.seek(0, 2)
    line = ''
    while True:
        tmp = file.readline()
        # Check if file has been rotated
        try:
            if os.stat(filename).st_ino != curino:
                new = open(filename, "r")
                file.close()
                file = new
                curino = os.fstat(file.fileno()).st_ino
                continue
        except IOError:
            # Current file dissappeared. Keep trying
            time.sleep(1)
            pass

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

    print("Tailing file: %s" % (log_file,))
    for line in follow(log_file):
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
                print("Finding Docker API...")
                client = docker.from_env()
                print("Finding miner container...")
                miner_container = client.containers.get("miner")
                cmd = "miner peer refresh %s" % (peer,)
                print("Execing %s..." % (cmd,))
                result = miner_container.exec_run(cmd)
                print(result)
