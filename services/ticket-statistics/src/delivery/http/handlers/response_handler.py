
def response(tag, message=None, data=None, metadata=None):
    if message is None:
        message = tag['message']

    response_dict = dict(status=tag['code'], message=message)
    if data is not None:
        response_dict['data'] = data
    if metadata is not None:
        response_dict['metadata'] = metadata
    return response_dict
