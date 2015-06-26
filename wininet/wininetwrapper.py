"""Module that acts as a wrapper for Windows Internet (WinINet) API.

Copyright 2014 Dario B. darizotas at gmail dot com
This software is licensed under a new BSD License. 
Unported License. http://opensource.org/licenses/BSD-3-Clause
"""

# windll and oledll
from ctypes import *
# Windows specific data types
from ctypes.wintypes import *

wininet = windll.LoadLibrary('wininet.dll')

# http://msdn.microsoft.com/en-us/library/windows/desktop/aa385384%28v=vs.85%29.aspx
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa383751%28v=vs.85%29.aspx#LPTSTR

# Option flags
# http://msdn.microsoft.com/en-us/library/aa385328%28v=vs.85%29.aspx
INTERNET_OPTION_PER_CONNECTION_OPTION = 75
INTERNET_OPTION_SETTINGS_CHANGED = 39
INTERNET_OPTION_REFRESH = 37

# Undocumented Internet Options constant values
# The meaning of them it is documented in the INTERNET_PER_CONN_OPTION structure
INTERNET_PER_CONN_FLAGS = 1
INTERNET_PER_CONN_PROXY_SERVER = 2
INTERNET_PER_CONN_PROXY_BYPASS = 3
INTERNET_PER_CONN_AUTOCONFIG_URL = 4
INTERNET_PER_CONN_AUTODISCOVERY_FLAGS = 5
INTERNET_PER_CONN_AUTOCONFIG_SECONDARY_URL = 6
INTERNET_PER_CONN_AUTOCONFIG_RELOAD_DELAY_MINS = 7
INTERNET_PER_CONN_AUTOCONFIG_LAST_DETECT_TIME = 8
INTERNET_PER_CONN_AUTOCONFIG_LAST_DETECT_URL = 9
INTERNET_PER_CONN_FLAGS_UI = 10

# Undocumented Proxy options constants
# Direct
PROXY_TYPE_DIRECT = 0x00000001
# Via named proxy
PROXY_TYPE_PROXY = 0x00000002
# Autoproxy URL
PROXY_TYPE_AUTO_PROXY_URL = 0x00000004
# Use autoproxy detection
PROXY_TYPE_AUTO_DETECT = 0x00000008

# c_char_p vs POINTER(c_char)
# http://stackoverflow.com/questions/6697065/whats-the-difference-between-lp-pointers-and-p-pointers-in-ctypes-and-wei
# http://stackoverflow.com/questions/11372391/casting-a-c-char-p-to-a-c-char-array

# INTERNET_PER_CONN_OPTION structure
# http://msdn.microsoft.com/en-us/library/aa385145%28v=vs.85%29.aspx
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa385145%28v=vs.85%29.aspx
class INTERNET_PER_CONN_OPTION(Structure):
    class Value(Union):
        _fields_ = [
            ('dwValue', DWORD),
            ('pszValue', c_char_p),
            ('ftValue', FILETIME),
            ]

    _fields_ = [
        ('dwOption', DWORD),
        ('Value', Value),
        ]
    
# INTERNET_PER_CONN_OPTION_LIST structure
# http://msdn.microsoft.com/en-us/library/aa385146%28v=vs.85%29.aspx
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa385146%28v=vs.85%29.aspx
class INTERNET_PER_CONN_OPTION_LIST(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('pszConnection', c_char_p),
        ('dwOptionCount', DWORD),
        ('dwOptionError', DWORD),
        ('pOptions', POINTER(INTERNET_PER_CONN_OPTION)),
        ]

# HINTERNET handles
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa383766%28v=vs.85%29.aspx
HINTERNET = LPVOID
    
# InternetSetOption prototype
# http://msdn.microsoft.com/en-us/library/aa385114%28v=vs.85%29.aspx
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa385114%28v=vs.85%29.aspx
InternetSetOption = wininet.InternetSetOptionA
InternetSetOption.argtypes = [HINTERNET, DWORD, LPVOID, DWORD]
InternetSetOption.restype  = BOOL

# InternetQueryOption prototype
# http://msdn.microsoft.com/en-us/library/aa385101%28v=vs.85%29.aspx
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa385101%28v=vs.85%29.aspx
InternetQueryOption = wininet.InternetQueryOptionA
InternetQueryOption.argtypes = [HINTERNET, DWORD, LPVOID, POINTER(DWORD)]
InternetQueryOption.restype  = BOOL
