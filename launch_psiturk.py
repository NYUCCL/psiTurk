#!/usr/bin/env python
# myapp.run

from psiturk_server import PsiTurkServer
import multiprocessing
from config import config

workers = multiprocessing.cpu_count() * 2 + 1
if __name__ == "__main__":
    loglevels = ["debug", "info", "warning", "error", "critical"]
    options = {
        'bind': config.get("Server Parameters", "host") + ":" + config.get("Server Parameters", "port"),
        'workers': str(multiprocessing.cpu_count() * 2 + 1),
        'loglevels': loglevels,
        'loglevel': loglevels[config.getint("Server Parameters", "loglevel")]
    }

PsiTurkServer(options).run()