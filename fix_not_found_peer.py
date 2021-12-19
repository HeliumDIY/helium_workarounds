#!/usr/bin/python3

import re
import requests
import subprocess
import time

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
    with open("/home/pi/miner_data/log/console.log", 'r') as file:
        file.seek(0, 2)
        for line in follow(file):
            m = re.match(r'.*failed to dial (?:challenger|proxy server) "(.*)":? not_found', line)
            print(line, end='')
            if m is not None:
                peer = m.group(1)
                # json_msg['params']['Addr'] = peer
                # print("Issuing request to miner to reload peer %s" % (peer,))
                # result = requests.post("http://localhost:4467", json=json_msg)
                # if result.status_code == 200:
                #     print("Success")
                # else:
                #     print("Error: (%d) %s" % (result.status_code, result.content))

                cmd = 'docker exec miner miner peer refresh %s' % (peer,)
                print("Running: %s" % (cmd,))
                split_cmd = cmd.split(' ')
                result = subprocess.check_output(split_cmd)
                print("Got: %s" % (result,))