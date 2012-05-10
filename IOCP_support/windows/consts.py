INVALID_HANDLE_VALUE = -1
  
IOC_WS2 = 0x08000000
IOC_OUT = 0x40000000
IOC_IN = 0x80000000
IOC_INOUT = IOC_IN | IOC_OUT
SIO_GET_EXTENSION_FUNCTION_POINTER =  IOC_INOUT | IOC_WS2 | 6
SOL_SOCKET = 0xffff
  
SO_PROTOCOL_INFOA = 0x2004
SO_PROTOCOL_INFOW = 0x2005
SO_UPDATE_ACCEPT_CONTEXT = 0x700B
SO_UPDATE_CONNECT_CONTEXT = 0x7010
  
WSA_IO_PENDING         = 997L
WSA_IO_INCOMPLETE      = 996L
WSA_INVALID_HANDLE     = 6L
WSA_INVALID_PARAMETER  = 87L
WSA_NOT_ENOUGH_MEMORY  = 8L
WSA_OPERATION_ABORTED  = 995L
  
WSAEINTR               = 10004L
WSAEBADF               = 10009L
WSAEACCES              = 10013L
WSAEFAULT              = 10014L
WSAEINVAL              = 10022L
WSAEMFILE              = 10024L
WSAEWOULDBLOCK         = 10035L
WSAEINPROGRESS         = 10036L
WSAEALREADY            = 10037L
WSAENOTSOCK            = 10038L
WSAEDESTADDRREQ        = 10039L
WSAEMSGSIZE            = 10040L
WSAEPROTOTYPE          = 10041L
WSAENOPROTOOPT         = 10042L
WSAEPROTONOSUPPORT     = 10043L
WSAESOCKTNOSUPPORT     = 10044L
WSAEOPNOTSUPP          = 10045L
WSAEPFNOSUPPORT        = 10046L
WSAEAFNOSUPPORT        = 10047L
WSAEADDRINUSE          = 10048L
WSAEADDRNOTAVAIL       = 10049L
WSAENETDOWN            = 10050L
WSAENETUNREACH         = 10051L
WSAENETRESET           = 10052L
WSAECONNABORTED        = 10053L
WSAECONNRESET          = 10054L
WSAENOBUFS             = 10055L
WSAEISCONN             = 10056L
WSAENOTCONN            = 10057L
WSAESHUTDOWN           = 10058L
WSAETOOMANYREFS        = 10059L
WSAETIMEDOUT           = 10060L
WSAECONNREFUSED        = 10061L
WSAELOOP               = 10062L
WSAENAMETOOLONG        = 10063L
WSAEHOSTDOWN           = 10064L
WSAEHOSTUNREACH        = 10065L
WSAENOTEMPTY           = 10066L
WSAEPROCLIM            = 10067L
WSAEUSERS              = 10068L
WSAEDQUOT              = 10069L
WSAESTALE              = 10070L
WSAEREMOTE             = 10071L
WSASYSNOTREADY         = 10091L
WSAVERNOTSUPPORTED     = 10092L
WSANOTINITIALISED      = 10093L
WSAEDISCON             = 10101L
WSAENOMORE             = 10102L
WSAECANCELLED          = 10103L
WSAEINVALIDPROCTABLE   = 10104L
WSAEINVALIDPROVIDER    = 10105L
WSAEPROVIDERFAILEDINIT = 10106L
WSASYSCALLFAILURE      = 10107L
WSASERVICE_NOT_FOUND   = 10108L
WSATYPE_NOT_FOUND      = 10109L
WSA_E_NO_MORE          = 10110L
WSA_E_CANCELLED        = 10111L
WSAEREFUSED            = 10112L
WSAHOST_NOT_FOUND      = 11001L
WSATRY_AGAIN           = 11002L
WSANO_RECOVERY         = 11003L
WSANO_DATA             = 11004L