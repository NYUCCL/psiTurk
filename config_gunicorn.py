
import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1

# Gunicorn doesn't like our import of config, so we wrap it in a funciton.
def from_config_file():
    global bind, errorlog, loglevel
    from config import config
    
    # Address to bind
    bind = config.get("Server Parameters", "host") + ":" + config.get("Server Parameters", "port")
    
    # Logging
    errorlog = config.get("Server Parameters", "logfile")
    loglevels = ["debug", "info", "warning", "error", "critical"]
    loglevel = loglevels[config.getint("Server Parameters", "loglevel")]
    
from_config_file()

print "Running on:", bind
print "Logging to:", errorlog
