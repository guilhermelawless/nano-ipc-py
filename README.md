# nano-ipc-py
A python library for interacting with the Nano currency node IPC.

The library's client accepts JSON serializable objects and returns a dictionary, deserialized from the node's JSON response.

**This code is experimental and not production tested. Use at your own risk.**

## Requirements
- Python 3
- Enabling the local IPC server in the node's config.json

## Setup

```bash
git clone https://github.com/guilhermelawless/nano-ipc-py.git && cd nano-ipc-py
python3 setup.py install --user
```

After setup you can remove the source folder `nano-ipc-py`.

## Using

```python
# imports the Client and custom Exceptions
import nano_ipc

# this is the default UNIX socket for the node's local IPC
server = '/tmp/nano'

# provides a persistent connection until c.close() is called
c = nano_ipc.Client(server, timeout=15)

# example request/response
req = {"action": "block_count"}
response = c.request(req)
print(response['unchecked'])
```

### For developers

An example is provided in `test/test_client.py` with custom error handling.
