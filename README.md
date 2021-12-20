# helium_workarounds
This builds a container where we can run scripts to try and workaround current bugs. The first one is `fix_not_found_peer.py`. This tails the miner logs looking
for not_found on lookups to peers or proxies and connects back to the container running the miner and asks the miner to refresh the peer.
