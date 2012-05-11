# -*- coding: utf-8 -*-


"""
ctypes implementation of a subset of win32api to using with iocp and winsockets
parts of this code was extracted from cogen progject: code.google.com/p/cogen
some functions was implemented by me for compatibility with win32file (win32api project)

@author: code.google.com/p/cogen
@modified by: caetano <marcelo at fiveti dot com>
@date 2012 may 10

"""
_ports_created = {}

import sys 
assert 'win32' in sys.platform

from ctypes import WINFUNCTYPE, GetLastError, windll, pythonapi, cast
from ctypes import create_string_buffer, c_ushort, c_ubyte, c_char, c_short,\
                   c_int, c_uint, c_ulong, c_long, c_void_p, byref, c_char_p,\
                   Structure, Union, py_object, POINTER, pointer, sizeof,\
                   string_at
                   
from ctypes.wintypes import HANDLE, ULONG, DWORD, BOOL, LPCSTR,\
                            LPCWSTR, WinError 
        
from msvcrt import get_osfhandle

import socket

from .consts import *

NULL =  c_ulong()
SOCKET = SIZE_T = c_uint
LPDWORD = POINTER(DWORD)
PULONG_PTR = POINTER(c_ulong)


class _US(Structure):
    _fields_ = [
                ("Offset", DWORD),
                ("OffsetHigh", DWORD)
                ]
    
class _U(Union):
    _fields_ = [
                ("s", _US),
                ("Pointer", c_void_p)
                ]
    _anonymous_ = ("s",)
    
class OVERLAPPED(Structure):
    _fields_ = [
                ("Internal", POINTER(ULONG)),
                ("InternalHIgh", POINTER(ULONG)),
                ("u", _U),
                ("hEvent", HANDLE),
                ("object", py_object)
                ]
    _anonymous_ = ("u",)

LPOVERLAPPED = POINTER(OVERLAPPED)

class WSABUF(Structure):
    _fields_ = [
                ("len", c_ulong),
                ("buf", c_char_p)
                ]
    
class GUID(Structure):
    _fields_ = [
                ('Data1', c_ulong),
                ('Data2', c_ushort),
                ('Data3', c_ushort),
                ('Data4', c_ubyte * 8),                                                
                ]
    def __init__(self, l, w1, w2, b1, b2, b3, b4, b5, b6, b7, b8):
        self.Data1 = l
        self.Data2 = w1
        self.Data3 = w2
        self.Data4[:] = (b1, b2, b3, b4, b5, b6, b7, b8)
        
WSAID_CONNECTEX = GUID(0x25a207b9,0xddf3,0x4660,0x8e,
                       0xe9,0x76,0xe5,0x8c,0x74,0x06,0x3e)
WSAID_ACCEPTEX = GUID(0xb5367df1,0xcbac,0x11cf,0x95,0xca,
                      0x00,0x80,0x5f,0x48,0xa1,0x92)
WSAID_TRANSMITFILE = GUID(0xb5367df0,0xcbac,0x11cf,0x95,
                          0xca,0x00,0x80,0x5f,0x48,0xa1,0x92)

MAX_PROTOCOL_CHAIN = 7
WSAPROTOCOL_LEN = 255

class WSAPROTOCOLCHAIN(Structure):
    _fields_ = [
        ('ChainLen', c_int),
        ('ChainEntries', DWORD * MAX_PROTOCOL_CHAIN)
    ]

class WSAPROTOCOL_INFO(Structure):
    _fields_ = [
        ('dwServiceFlags1', DWORD),
        ('dwServiceFlags2', DWORD),
        ('dwServiceFlags3', DWORD),
        ('dwServiceFlags4', DWORD),
        ('dwProviderFlags', DWORD),
        ('ProviderId', GUID),
        ('dwCatalogEntryId', DWORD),
        ('ProtocolChain', WSAPROTOCOLCHAIN),
        ('iVersion', c_int),
        ('iAddressFamily', c_int),
        ('iMaxSockAddr', c_int),
        ('iMinSockAddr', c_int),
        ('iSocketType', c_int),
        ('iProtocol', c_int),
        ('iProtocolMaxOffset', c_int),
        ('iNetworkByteOrder', c_int),
        ('iSecurityScheme', c_int),
        ('dwMessageSize', DWORD),
        ('dwProviderReserved', DWORD),
        ('szProtocol', c_char * (WSAPROTOCOL_LEN+1)),
    ]
  
class TRANSMIT_FILE_BUFFERS(Structure):
    _fields_ = [
        ('Head', c_void_p),
        ('HeadLength', DWORD),
        ('Tail', c_void_p),
        ('TailLength', DWORD)
    ]
  
class sockaddr(Structure):
    _fields_ = [
        ('sa_family', c_ushort),
        ('sa_data', c_char * 14)
    ]
  
ACCEPT_BUFF_SZ = 2*sizeof(sockaddr)
  
class in_addr(Structure):
    _fields_ = [
        ('s_b1', c_ubyte),
        ('s_b2', c_ubyte),
        ('s_b3', c_ubyte),
        ('s_b4', c_ubyte)
    ]
  
class sockaddr_in(Structure):
    _fields_ = [
        ('sin_family', c_ushort),
        ('sin_port', c_ushort),
        ('sin_addr', in_addr),
        ('sin_zero', c_char * 8)
    ]
  
class addrinfo(Structure):
    pass
  
addrinfo._fields_ = [
    ('ai_flags', c_int),
    ('ai_family', c_int),
    ('ai_socktype', c_int),
    ('ai_protocol', c_int),
    ('ai_addrlen', c_uint),
    ('ai_canonname', c_char_p),
    ('ai_addr', POINTER(sockaddr)),
    ('ai_next', POINTER(addrinfo))
]
  
addrinfo_p = POINTER(addrinfo)
  
def _error_throw(result, func, args):
    if result:
        raise WinError()
    return result
  
def _bool_error_throw(result, func, args):
    if not result:
        raise WinError()
    return result
  
def _error_check(result, func, args):
    if result:
        return GetLastError()
    return result
  
def _bool_error_check(result, func, args):
    if not result:
        return GetLastError()
    return 0
  
lowCreateIoCompletionPort = windll.kernel32.CreateIoCompletionPort
lowCreateIoCompletionPort.argtypes = (HANDLE, HANDLE, c_ulong, DWORD)
lowCreateIoCompletionPort.restype = HANDLE
lowCreateIoCompletionPort.errcheck = _bool_error_throw
def CreateIoCompletionPort(handle, existing, completionKey, numThreads):
    if existing == None:
        existing = 0
    ck = c_ulong(completionKey)
    fd =  lowCreateIoCompletionPort(handle, existing, ck, numThreads )
    return fd

"""
BOOL WINAPI GetQueuedCompletionStatus(
  __in   HANDLE CompletionPort,
  __out  LPDWORD lpNumberOfBytes,
  __out  PULONG_PTR lpCompletionKey,
  __out  LPOVERLAPPED *lpOverlapped,
  __in   DWORD dwMilliseconds
);
"""
"""
(int, int, int, PyOVERLAPPED) = GetQueuedCompletionStatus(hPort, timeOut )
rc, NumberOfBytesTransferred, CompletionKey, overlapped
"""
  
lowGetQueuedCompletionStatus = windll.kernel32.GetQueuedCompletionStatus
lowGetQueuedCompletionStatus.argtypes = (HANDLE, POINTER(DWORD), POINTER(c_ulong), 
                                      POINTER(LPOVERLAPPED), DWORD)
lowGetQueuedCompletionStatus.restype = BOOL
lowGetQueuedCompletionStatus.errcheck = _bool_error_check

def GetQueuedCompletionStatus(hPort, timeOut):
    overlapped = pointer(LPOVERLAPPED())
    nob = DWORD()
    
    ck = c_ulong()
    rc = lowGetQueuedCompletionStatus(hPort, pointer(nob), pointer(ck), 
                                 overlapped, timeOut)
    #return (rc, nob, ck, overlapped)
    overlapped = overlapped and overlapped.contents
    nob = nob.value
    ck = ck.value
    return (rc, nob, ck, overlapped)
    
    
    
  
PostQueuedCompletionStatus = windll.kernel32.PostQueuedCompletionStatus
# BOOL = HANDLE CompletionPort, DWORD dwNumberOfBytesTransferred, ULONG_PTR dwCompletionKey, LPOVERLAPPED lpOverlapped
PostQueuedCompletionStatus.argtypes = (HANDLE, DWORD, 
                                       POINTER(c_long), POINTER(OVERLAPPED))
PostQueuedCompletionStatus.restype = BOOL
PostQueuedCompletionStatus.errcheck = _bool_error_check
  
CancelIo = windll.kernel32.CancelIo
# BOOL = HANDLE hFile
CancelIo.argtypes = (HANDLE,)
CancelIo.restype = BOOL
CancelIo.errcheck = _bool_error_check
  
getaddrinfo = windll.ws2_32.getaddrinfo
# int = const char *nodename, const char *servname, const struct addrinfo *hints, struct addrinfo **res
getaddrinfo.argtypes = (c_char_p, c_char_p, POINTER(addrinfo), 
                        POINTER(POINTER(addrinfo)))
getaddrinfo.restype = c_int
getaddrinfo.errcheck = _error_throw
  
getsockopt = windll.ws2_32.getsockopt
# int = SOCKET s, int level, int optname, char *optval, int *optlen
getsockopt.argtypes = (SOCKET, c_int, c_int, c_char_p, POINTER(c_int))
getsockopt.restype = c_int
getsockopt.errcheck = _error_throw
  
WSARecv = windll.ws2_32.WSARecv
# int = SOCKET s, LPWSABUF lpBuffers, DWORD dwBufferCount, LPDWORD lpNumberOfBytesRecvd, LPDWORD lpFlags, LPWSAOVERLAPPED lpOverlapped, LPWSAOVERLAPPED_COMPLETION_ROUTINE lpCompletionRoutine
WSARecv.argtypes = (SOCKET, POINTER(WSABUF), DWORD, POINTER(DWORD),
                     POINTER(DWORD), POINTER(OVERLAPPED), c_void_p)
WSARecv.restype = c_int
WSARecv.errcheck = _error_check
  
WSASend = windll.ws2_32.WSASend
# int = SOCKET s, LPWSABUF lpBuffers, DWORD dwBufferCount, LPDWORD lpNumberOfBytesSent, DWORD dwFlags, LPWSAOVERLAPPED lpOverlapped, LPWSAOVERLAPPED_COMPLETION_ROUTINE lpCompletionRoutine
WSASend.argtypes = (SOCKET, POINTER(WSABUF), DWORD, POINTER(DWORD),
                     DWORD, POINTER(OVERLAPPED), c_void_p)
WSASend.restype = c_int
WSASend.errcheck = _error_check
  
lowAcceptEx = windll.Mswsock.AcceptEx
"""
BOOL AcceptEx(
  __in   SOCKET sListenSocket,
  __in   SOCKET sAcceptSocket,
  __in   PVOID lpOutputBuffer,
  __in   DWORD dwReceiveDataLength,
  __in   DWORD dwLocalAddressLength,
  __in   DWORD dwRemoteAddressLength,
  __out  LPDWORD lpdwBytesReceived,
  __in   LPOVERLAPPED lpOverlapped
);
"""
lowAcceptEx.argtypes = (SOCKET, SOCKET, c_void_p, DWORD, DWORD, DWORD,
                      POINTER(DWORD), POINTER(OVERLAPPED))
lowAcceptEx.restype = BOOL
lowAcceptEx.errcheck = _bool_error_check

"""
Added Function to looks like win32file function 
"""

def AcceptEx(sListening, sAccepting, buffer, ol):
    tLis = type(sListening)
    tAcc = type(sAccepting)
    if tLis == socket.socket:
        fdLis = sListening.fileno()
    elif tLis is int:
        fdLis = sListening
    else:
        raise TypeError, "Can't accept type '%s' for argument 1" % str(tLis)

    
    if tAcc == socket.socket:
        fdAcc = sAccepting.fileno()
    elif tAcc is int:
        fdAcc = sAccepting
    else:
        raise TypeError, "Can't accept type %s for argument 2" % str(tAcc)
    
    prot_info = WSAPROTOCOL_INFO()
    prot_info_len = c_int(sizeof(prot_info))
    nbytes = c_ulong()
    
    getsockopt(fdLis, SOL_SOCKET, SO_PROTOCOL_INFOA,
                cast(byref(prot_info), c_char_p),
                byref(prot_info_len))
                
    
    return bool(lowAcceptEx(fdLis, fdAcc,
                    cast(buffer, c_void_p),
                    0,
                    prot_info.iMaxSockAddr + 16,
                    prot_info.iMaxSockAddr + 16,
                    nbytes,
                    pointer(ol)))

  
lowGetAcceptExSockaddrs = windll.Mswsock.GetAcceptExSockaddrs

lowGetAcceptExSockaddrs.argtypes = (c_void_p, DWORD, DWORD, DWORD,
                                  POINTER(sockaddr), POINTER(c_int),
                                   POINTER(sockaddr), POINTER(c_int))
lowGetAcceptExSockaddrs.restype = None
"""
(iFamily, LocalSockAddr , RemoteSockAddr ) = GetAcceptExSockaddrs(sAccepting, buffer )

"""
"""
void GetAcceptExSockaddrs(
  __in   PVOID lpOutputBuffer,
  __in   DWORD dwReceiveDataLength,
  __in   DWORD dwLocalAddressLength,
  __in   DWORD dwRemoteAddressLength,
  __out  LPSOCKADDR *LocalSockaddr,
  __out  LPINT LocalSockaddrLength,
  __out  LPSOCKADDR *RemoteSockaddr,
  __out  LPINT RemoteSockaddrLength
);
"""
def GetAcceptExSockaddrs(sAccepting, buffer):
    
    prot_info = WSAPROTOCOL_INFO()
    prot_info_len = c_int(sizeof(prot_info))
    nbytes = c_ulong()
    
    local_sock = pointer(sockaddr())
    remote_sock = pointer(sockaddr())
    local_sock_len = pointer(c_int())
    remote_sock_len = pointer(c_int())
    
    getsockopt(sAccepting.fileno(), SOL_SOCKET, SO_PROTOCOL_INFOA,
                cast(byref(prot_info), c_char_p),
                byref(prot_info_len))

    
    lowGetAcceptExSockaddrs(
                            cast(buffer, c_void_p),
                            DWORD(len(buffer)),
                            DWORD((sizeof(sockaddr_in) + 16) * 2),
                            DWORD((sizeof(sockaddr_in) + 16) * 2),
                            local_sock,
                            local_sock_len,
                            remote_sock,
                            remote_sock_len
                            )
    
    #todo get addrs by socket functions
    local_sock = local_sock and local_sock.contents
    remote_sock = remote_sock and remote_sock.contents
    local_sock_len = local_sock_len.contents.value
    remote_sock_len = remote_sock_len.contents.value
    
    return (local_sock, remote_sock, local_sock_len, remote_sock_len)
    
  
# int = SOCKET s, DWORD dwIoControlCode, LPVOID lpvInBuffer, DWORD cbInBuffer, LPVOID lpvOutBuffer, DWORD cbOutBuffer, LPDWORD lpcbBytesReturned, LPWSAOVERLAPPED lpOverlapped, LPWSAOVERLAPPED_COMPLETION_ROUTINE lpCompletionRoutine
WSAIoctl = windll.ws2_32.WSAIoctl
WSAIoctl.argtypes = (SOCKET, DWORD, c_void_p, DWORD, c_void_p, DWORD,
                      POINTER(DWORD), POINTER(OVERLAPPED), c_void_p)
WSAIoctl.restype = c_int
WSAIoctl.errcheck = _error_throw
  
# BOOL = SOCKET s, const struct sockaddr *name, int namelen, PVOID lpSendBuffer, DWORD dwSendDataLength, LPDWORD lpdwBytesSent, LPOVERLAPPED lpOverlapped
ConnectExType = WINFUNCTYPE(BOOL, c_int, POINTER(sockaddr), c_int, c_void_p, 
                            DWORD, POINTER(DWORD), POINTER(OVERLAPPED))
  
def _GetConnectExPtr(given_socket=None):
    from socket import socket
    bogus_sock = given_socket or socket()
    bogus_bytes = DWORD()
    ConnectEx = ConnectExType(0)
    ret = WSAIoctl(
        bogus_sock.fileno(), SIO_GET_EXTENSION_FUNCTION_POINTER, 
        byref(WSAID_CONNECTEX), sizeof(WSAID_CONNECTEX),
        byref(ConnectEx), sizeof(ConnectEx), byref(bogus_bytes), None, None
    )
    return ConnectEx
  
ConnectEx = _GetConnectExPtr()
ConnectEx.errcheck = _bool_error_check
  
#~ BOOL = SOCKET hSocket, HANDLE hFile, DWORD nNumberOfBytesToWrite, DWORD nNumberOfBytesPerSend, LPOVERLAPPED lpOverlapped,LPTRANSMIT_FILE_BUFFERS lpTransmitBuffers, DWORD dwFlags
TransmitFileType = WINFUNCTYPE(BOOL, SOCKET, HANDLE, DWORD, DWORD, 
                               POINTER(OVERLAPPED),
                                POINTER(TRANSMIT_FILE_BUFFERS), DWORD)
  
def _GetTransmitFilePtr(given_socket=None):
    from socket import socket
    bogus_sock = given_socket or socket()
    bogus_bytes = DWORD()
    TransmitFile = TransmitFileType(0)
    ret = WSAIoctl(
        bogus_sock.fileno(), SIO_GET_EXTENSION_FUNCTION_POINTER,
        byref(WSAID_TRANSMITFILE), sizeof(WSAID_TRANSMITFILE),
        byref(TransmitFile), sizeof(TransmitFile),
        byref(bogus_bytes), None, None
    )
    return TransmitFile
  
TransmitFile = _GetTransmitFilePtr()
TransmitFile.errcheck = _bool_error_check
  
CloseHandle = windll.kernel32.CloseHandle
CloseHandle.argtypes = (HANDLE,)
CloseHandle.restype = BOOL
  
_get_osfhandle = windll.msvcr71._get_osfhandle
_get_osfhandle.argtypes = (c_int,)
_get_osfhandle.restype = c_long
  
# Python API
  
pythonapi.PyBuffer_New.argtypes = (c_ulong,)
pythonapi.PyBuffer_New.restype = py_object
AllocateBuffer = lambda n: create_string_buffer(n) 
  
pythonapi.PyErr_SetFromErrno.argtypes = (py_object,)
pythonapi.PyErr_SetFromErrno.restype = py_object

testing = True 

if testing:

    def test():
        print "creating listening socket"
        s = socket.socket(); s1 = socket.socket()
        print "listening on port 1234"
        s.bind(("",1234))
        s.listen(200)
        hPort = CreateIoCompletionPort(INVALID_HANDLE_VALUE,
                                      None, 0, 0)
        def accept(s1, buff):
            import struct
            rc, nb, ck, ol = GetQueuedCompletionStatus(hPort, -1)
            s1.setsockopt(
                          socket.SOL_SOCKET,
                          SO_UPDATE_ACCEPT_CONTEXT,
                          struct.pack("I", s.fileno())
                          )
            assert ck == 15 , 'invalid ck'
            return (rc, nb, ck, ol),s1
        
        buff = AllocateBuffer(64)
        overlapped = OVERLAPPED()
        s1 = socket.socket()
        AcceptEx(s, s1, buff, overlapped )
        print CreateIoCompletionPort(s.fileno(), hPort, 15, 0) == hPort, hPort
        
        
        #out.append((s1, buff, overlapped))
    
        print "please connect on port 1234"
        return accept(s1, buff)
     
  
  