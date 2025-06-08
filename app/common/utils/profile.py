from functools import wraps

from pyinstrument import Profiler


def profile_api(print_output: bool = True, unicode: bool = True, color: bool = True):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            profiler = Profiler()
            profiler.start()

            result = await func(*args, **kwargs)

            profiler.stop()
            if print_output:
                print(profiler.output_text(unicode=unicode, color=color))
            return result

        return wrapper

    return decorator
