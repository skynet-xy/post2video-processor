import multiprocessing

# Number of worker processes
# A common formula is (2 x $num_cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class to use
worker_class = 'uvicorn.workers.UvicornWorker'

# Host and port
bind = '0.0.0.0:8000'

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Timeout settings
timeout = 120
keepalive = 5