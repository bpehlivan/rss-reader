# converts a dictionary to an object
class DictToObject:
    def __init__(self, dictionary):
        for key in dictionary:
            value = dictionary[key]
            if isinstance(value, dict):
                value = DictToObject(value)
            self.__dict__[key] = value

    def __getattr__(self, attr):
        return self.__dict__.get(attr, None)
