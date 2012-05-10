"""
IOCP implementation for windows

We implement simple and usable support for Windows IOCP on Python.
Our module has no external dependencies. 
It only uses ctypes and works by patching the built-in socket class on runtime.

to use it, just run register function, and the IOCP class will appear on select
module.

@author Marcelo Aires Caetano
@email <marcelo at fiveti dot com>
@date 2012 may 10 
"""
"""
Copyright (c) 2012 caetano

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

def register(cached_acceptors=128):
    """
    register the IOCP class on the select module, patch the builtin socket class
    in runtime,
    previously sockets created will be modified to transparently
    
    :param cached_acceptors: the number of sockets acceptors pre-loaded when
    you listen to a socket. 
    """
    from .windows import WinSockets
    WinSockets._Winsock.MAX_CACHED_SOCKETS = [cached_acceptors]
    from ._iocp_windows import IOCP
    from ._iocp_windows import IOCPError
    import select as _select
    _select.IOCP = IOCP
    _select._select = _select.select
    
    def select(rlist, wlist, xlist, timeout=None):
        #runtime patching for select function
        try:
            for i in rlist + wlist + xlist:
                assert not i.using_iocp
        except AssertionError:
            raise IOCPError, "can't select a iocp registered socket."
        
        return _select._select(rlist, wlist, xlist, timeout)
    
    select.__doc__ = _select._select.__doc__
    select.__name__ = _select._select.__name__
    _select.select = select
    