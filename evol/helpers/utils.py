from inspect import signature


def select_arguments(func):
    """Decorate a function such that it accepts any keyworded arguments.

    The resulting function accepts any arguments, but only arguments that
    the original function accepts are passed. This allows keyworded 
    arguments to be passed to multiple (decorated) functions, even if they
    do not (all) accept these arguments.

    :param func: Function to decorate.
    :return: Callable
    """
    def result(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError:
            return func(*args, **{k: v for k, v in kwargs.items() if k in signature(func).parameters})
    return result
