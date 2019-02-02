import nano_ipc


if __name__ == "__main__":
    server_address = '/tmp/nano'
    requests = [
        {"action": "version"},
        {"action": "block_count"}
    ]
    try:
        client = nano_ipc.Client(server_address, timeout=15)
    except nano_ipc.ConnecionFailure as e:
        print(e)
    else:
        for request in requests:
            try:
                response = client.request(request)
                print("Request:\n\t{}\nResponse:\n\t{}\n\n----\n".format(request, response))
            except nano_ipc.BadResponse as e:
                # print(e.response_raw)
                print(e)
            except nano_ipc.IPCError as e:
                print(e)
