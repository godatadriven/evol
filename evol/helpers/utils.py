from inspect import signature


def select_arguments(func):
    def result(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError:
            return func(*args, **{k: v for k, v in kwargs.items() if k in signature(func).parameters})
    return result
