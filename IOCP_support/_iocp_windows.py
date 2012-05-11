"""
IOCP implementation for windows

We implement simple and usable support for Windows IOCP on Python.
Our module has no external dependencies. 
It only uses ctypes and works by patching the built-in socket class on runtime.

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
import sys 

assert 'win32' in sys.platform

from .windows import winfile_api

#used to patch the runtime builtin-socket implementation
#don't remove that import
from .windows import WinSockets

import socket


class IOCPError(Exception):
    pass

class IOCP(object):
    
    _id = 0
    
    @property
    def identification(self):
        self._id = (self._id + 1) & 0xFFFFFFFF
        return self._id
    
    def __init__(self, threads=0):
        self.iocp = winfile_api.CreateIoCompletionPort(
                                            winfile_api.INVALID_HANDLE_VALUE,
                                                    None, 0, 0)
        self._file_descriptors = {}
        self._file_descriptors_key = {}
        self._file_descriptors_fd = {}
        self._pending_events = []
        
    
    def register(self, fd):
        is_socket = False
        
        if type(fd) == file:
            handle = fd.fileno()
        elif type(fd) == socket.socket:
            handle = fd.fileno()
            is_socket = True
        else:
            raise TypeError, "invalid fd"
        
        if is_socket:
            fd._winsockets.using_iocp = True
            fd._winsockets.iocp = self
            if fd._winsockets.listening:            
                fd._winsockets.perform_accept_ex()      
            
        key = self.identification
        winfile_api.CreateIoCompletionPort(handle, self.iocp, key, 0)
        self._file_descriptors[fd] = (handle, key)
        self._file_descriptors_key[key] = handle
        self._file_descriptors_fd[handle] = fd
        
    def unregister(self, fd):
        if fd not in self._file_descriptors:
            raise IOCPError
        key, handle = self._file_descriptors[fd]
        winfile_api.CancelIo(handle)
        del self._file_descriptors[fd]
        del self._file_descriptors_key[key]
        del self._file_descriptors_fd[handle]
        fd._winsock.unregister_iocp()
        
        
        
    def _poll(self, timeout=None):
        if timeout == None:
            timeout=-1
        if self._file_descriptors:
            _, _, key,_ = winfile_api.GetQueuedCompletionStatus(self.iocp,timeout)
            try:
                handle =  self._file_descriptors_key[key]
                return self._file_descriptors_fd[handle]
            except KeyError:
                return None
            
    def poll(self, timeout=None, _last_event=False):
        evt = self._poll(timeout)
        if not self._pending_events:
            if evt:
                self._pending_events.append(self._poll(timeout))
        try:
            if not _last_event:
                return self._pending_events[0]
            else:
                return self._pending_events[-1]
        except IndexError:
            return None
            
    
    def _wait_event(self, fd, timeout=None):
        """
        wait for a event on fd on timeout, if timeout=None, waits forever
        when event occurs, the function should return True.
        and the event is poped from the event_list
        if the timeout expires and there is no event, should return False
        """
        try: 
            self._file_descriptors[fd]
        except KeyError:
            raise IOCPError, "the fd '%s' is not monitored by IOCP" % repr(fd)
        
        if fd in self._pending_events:
            del self._pending_events[self._pending_events.index(fd)]
            return True
        
        if not timeout:
            while 1:
                if self.poll(_last_event=True) == fd:
                    self._pending_events.pop()
                    return
        if timeout:
            if self.poll(timeout, True) == fd:
                return True
            return False
        
    def close(self):
        """
        unregister all fds registereds
        """
        for i in self._file_descriptors.copy():
            self.unregister(i)
    
    def __del__(self):
        winfile_api.CancelIo(self.iocp)

        
            
testing = False 

if testing:            
    s = socket.socket()
    iocp = IOCP() 
    s.bind(("",1234))   
    s.listen(1)
    iocp.register(s)
    print "please connect in localhost:1234 cuz i'm waiting, niggar "
    n = iocp.poll()
    b = n.accept()
    print b        
    v, _ = b
    v.send("oi")
            