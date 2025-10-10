# IBR-DTN Quick Test

Install `ibrdtn-tools` on two devices (A/B). Configure different `net.eid`.

```
# Node A
ibrdtnd -c ibrdtn.conf.example
# Send bundle to B
dtnsend -r dtn://nodeB/inbox -p text/plain -d "hola" -t 60

# Node B (in another shell)
dtnrecv -s inbox
```
