def find(type, collection):
    for item in collection:
        if isinstance(item, type):
            return item
    return None
