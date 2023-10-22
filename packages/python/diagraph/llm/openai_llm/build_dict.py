RecursiveDict = dict[str, "str | RecursiveDict"]


def for_key(delta: RecursiveDict):
    for key in delta.keys():
        if delta.get(key) is not None:
            yield key


def check_types(
    response: RecursiveDict | str | None, delta: RecursiveDict | str | None,
) -> None:
    if response is not None and delta is not None and type(response) != type(delta):
        raise Exception(f"Type mismatch: {type(response)} {type(delta)}")


def build_dict(response: RecursiveDict, delta: RecursiveDict):
    for key in for_key(delta):
        delta_val = delta[key]  # this is guaranteed to exist because of for_key
        check_types(response.get(key), delta_val)
        if type(delta_val) is str:
            response[key] = response.get(key, "") + delta_val
        else:
            response[key] = build_dict(response.get(key, {}), delta_val)
    return response
