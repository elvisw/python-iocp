**This project is in _ALPHA_ stage by now**

This project currently supports only sockets and lacks to notify reading, but it is in progress, come again later to check the new features to this project.

We implement simple and usable support for Windows IOCP on Python. Our module has no external dependencies. It only uses ctypes and works by patching the built-in socket class on runtime.

Example code:

```
import IOCP_support
IOCP_support.register()
import select

iocp = select.IOCP()

iocp.register(my_socket)
iocp.register(my_pipe)
iocp.register(my_named_pipe)
iocp.register(my_any_fd)
iocp.register(my_directory_watcher)

fd = iocp.poll()

iocp.unregister(anything_registered)
```

IOCP appears in the select module just like epoll and kqueue would appear.

Don't forget to close iocp before deleting it, otherwise it won't be collected by the GC.

```
iocp.close()
del iocp
```
