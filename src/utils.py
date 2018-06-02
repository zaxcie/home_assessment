def try_catch_empty_dict(func):
    def function_wrapper(x):
        try:
            func(x)
        except:
            return dict()
    return function_wrapper