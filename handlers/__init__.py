import handlers
import handlers.start
import handlers.admin
import handlers.files

routers = [handlers.start.router, handlers.admin.router, handlers.files.router]
