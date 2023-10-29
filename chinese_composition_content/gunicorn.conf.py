# 并行工作进程数
workers = 1

# 监听
bind = '0.0.0.0:8003'

# 设置守护进程,将进程交给supervisor管理
# daemon = 'false'

# 工作模式协程
# worker_class = 'gevent'

# 设置访问日志和错误信息日志路径
# accesslog = '/var/log/gunicorn_acess.log'
# errorlog = '/var/log/gunicorn_error.log'

# 设置日志记录水平
# loglevel = 'info'

timeout = 300
