
class LoadBalancer:
    def __init__(self):
        pass

    def new(klass, *args, **kwargs):
        # TODO: validate that args, kwargs are pickleable
        return Proxy(klass, args, kwargs)


