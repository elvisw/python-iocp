"""
This file is used only to  patching the builtin sockets library
on windows to support iocp.
you just need to import that, and not to call nothing of this content

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

__all__ = []
import sys 
import os

assert os.name == 'nt'
from types import MethodType

import socket as _socket
from socket import socket

from .winfile_api import AllocateBuffer, OVERLAPPED, GetAcceptExSockaddrs,\
                         AcceptEx, SO_UPDATE_ACCEPT_CONTEXT, WSASocket


import struct


def using_iocp(self):
    return self._winsockets.using_iocp


def _winsockets(self):
    """
    runtime selfpatching
    """
    try:
        self.recvfrom_into.using_iocp
    except:
        """
        not registered inside object _winsocket yet.
        """
        __name__ = self.recvfrom_into.__name__
        __doc__ = self.recvfrom_into.__doc__
        self.recvfrom_into = _Winsock(self)
        self.recvfrom_into.__name__ = __name__
        self.recvfrom_into.__doc__ = __doc__
        for i in self.recvfrom_into.patch_after_registering:
            name = i.__name__
            func = MethodType(i, self, socket)
            setattr(self, name, func)
        
    return self.recvfrom_into

socket.using_iocp = property(using_iocp)
socket._winsockets = property(_winsockets)
socket._sock_recv = socket.recv
socket._sock_accept = socket.accept
socket._sock_listen = socket.listen

class _Winsock(object):
    __slots__ = ['using_iocp', 'iocp', 'listening', 'listening_n', 'acceptors',
                 'MAX_CACHED_SOCKETS', 'socket', 'max_cached_sockets_n',
                 'patch_after_registering', '__name__','__doc__']
    MAX_CACHED_SOCKETS = [1] #max number of pre-accepted sockets
    def __init__(self, socket):
        
        self.patch_after_registering = [recv]
        self.max_cached_sockets_n = 0 
        self.using_iocp = False
        self.listening = False
        self.listening_n = 0
        self.acceptors = []
        self.iocp = None
        self.socket = socket
        self.__name__ = ''
        self.__doc__ = ''
        
    def __call__(self, self_socket, *args, **kw):
        return self_socket._sock.recvfrom_into(*args, **kw)
    
    def perform_accept_ex_addrs(self):
        s1, buf, ol = self.acceptors.pop()
        print s1
        s1.setsockopt(
            _socket.SOL_SOCKET,
            SO_UPDATE_ACCEPT_CONTEXT,
            struct.pack("I", self.socket.fileno())
        )
        #TODO
        GetAcceptExSockaddrs(self.socket, buf)
        
        #checking if the cache is null, if, repopulate cache
        self.perform_accept_ex()
        s1 = socket(_sock=s1)
        return (s1, s1.getpeername())

    
    def perform_accept_ex(self):
        """
        maintain a cache of preallocated sockets for faster accepting sockets
        """

         
        if self.listening_n == 0:
            self.listening_n = self.MAX_CACHED_SOCKETS[0]
        if not self.max_cached_sockets_n:
            if self.listening_n > self.MAX_CACHED_SOCKETS[0]:
                self.max_cached_sockets_n = self.MAX_CACHED_SOCKETS[0]
            else:
                self.max_cached_sockets_n = self.listening_n
        if not self.acceptors:
            print "performing acceptors"
            while len(self.acceptors) < self.max_cached_sockets_n:
                s = self.socket
                print "creating acceptor,",
                #s1 = WSASocket(s.family, s.type)
                s1 = _socket._realsocket(s.family, s.type)
                buff = AllocateBuffer(128)
                overlapped = OVERLAPPED()
                AcceptEx(s.fileno(), s1.fileno(), buff, overlapped )
                self.acceptors.append((s1,buff, overlapped))
             
                
                
    def perform_wait_event(self):
        timeout = self.socket.gettimeout()
        print timeout
        print self.iocp._wait_event(self.socket, timeout)
            

    def unregister_iocp(self):
        self.using_iocp = False
        self.iocp = None
        del self.acceptors
        self.acceptors = []
        

def accept(self):
    """
    Perform accept on a socket, if using iocp use windows magics
    """
    if self.using_iocp:
        print "waiting event"
        self._winsockets.perform_wait_event()
        r = self._winsockets.perform_accept_ex_addrs()
        return r
    else:
        return self._sock_accept()

def listen(self, value):
    self._winsockets.listening = True
    self._winsockets.listening_n = value
    r = self._sock_listen(value)
    if self.using_iocp:
        self._winsockets.perform_accept_ex()
    return r

def recv(self, value):
    if self.using_iocp:
        self._winsockets.perform_wait_event()
    return self._sock_recv(value)


socket.accept = MethodType(accept, None, socket)
socket.listen = MethodType(listen, None, socket)
#socket.recv = MethodType(recv, None, socket)