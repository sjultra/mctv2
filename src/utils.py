from logger import log

def stage(stage_name):
    def decorator(func):
        def wrapper(*args):
            log.info("Started stage: {}".format(stage_name))
            return_val = func(*args)
            return return_val
        return wrapper
    return decorator

