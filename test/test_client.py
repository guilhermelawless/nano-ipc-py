import asyncio
import nano_ipc
import json
from sys import argv, exit
from time import perf_counter


async def handle_response(request, response, no_print=False):
    response = await response
    if not no_print:
        print("Request:\n\t{}\nResponse:\n\t{}\n\n----\n".format(request, response))


async def test_requests(client, requests, loop=asyncio.get_event_loop()):

    # If not using this idiom, client.connect() and client.close() should be called and awaited on
    async with client:
        tasks = [loop.create_task(handle_response(request, client.request(request))) for request in requests]
        await asyncio.gather(*tasks)

        # a lot more tasks now
        N = 1000
        print('Doing {} requests silently'.format(N*len(requests)))
        start = perf_counter()
        crazy_requests = requests * N
        crazy_tasks = [loop.create_task(handle_response(request, client.request(request), no_print=True)) for request in crazy_requests]
        await asyncio.gather(*crazy_tasks)
        print('Done in {:.0f} ms'.format(1e3*(perf_counter() - start)))

if __name__ == "__main__":
    argc = len(argv)
    if argc > 2:
        server_address = (argv[1], argv[2])
    elif argc > 1:
        server_address = argv[1]
    else:
        print("Usage: {} [path|host port]".format(argv[0]))
        exit(1)

    print('Requesting from {}'.format(server_address))
    requests = [
        {"action": "version"},
        {"action": "block_count"},
        {"action": "uptime"}
    ]

    loop = asyncio.get_event_loop()
    client = nano_ipc.Client(server_address, max_connections=10, timeout=5)
    loop.run_until_complete(test_requests(client, requests))
