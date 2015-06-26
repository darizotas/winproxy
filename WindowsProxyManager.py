"""Class that manages the Internet proxy configuration.

Copyright 2014 Dario B. darizotas at gmail dot com
This software is licensed under a new BSD License. 
Unported License. http://opensource.org/licenses/BSD-3-Clause
"""
from wininet.winproxysettings import *
from lxml import etree
import sys, os
import argparse

class WindowsProxyManager:
    """Class that manages the changes to the Internet proxy settings.
    See also:
    https://stackoverflow.com/questions/18117652/how-to-use-ctypes-windll-wininet-internetqueryoptionw-in-python
    """

    def __init__(self):
        """Initialises the Internet proxy settings.
        """
        self.settings = WinProxySettings()
        
    def disable(self):
        """Disables Internet proxy settings or access directly to Internet.
        """
        print 'Disabling Internet Proxy...'
        option = {INTERNET_PER_CONN_FLAGS: PROXY_TYPE_DIRECT}
        return self._change(option)
    
    def current(self, file):
        """Prints current Internet proxy settings.
        """
        option = (INTERNET_PER_CONN_OPTION * 5)()
        option[0].dwOption = INTERNET_PER_CONN_FLAGS
        option[1].dwOption = INTERNET_PER_CONN_AUTOCONFIG_URL
        option[2].dwOption = INTERNET_PER_CONN_PROXY_SERVER
        option[3].dwOption = INTERNET_PER_CONN_PROXY_BYPASS
        option[4].dwOption = INTERNET_PER_CONN_AUTODISCOVERY_FLAGS
        
        if self.settings.current(option):
            print 'Current Internet Proxy options:'
            print 'Proxy type:          %i' % option[0].Value.dwValue
            print 'Autoconfig URL:      %s' % option[1].Value.pszValue
            print 'Static Proxy server: %s' % option[2].Value.pszValue
            print 'Proxy bypass URLs:   %s' % option[3].Value.pszValue
            #print 'Autodetect:          %i' % option[4].Value.dwValue
            
            if file:
                try:
                    f = open(file, 'w')
                    f.write('<settings>\n')
                    f.write('    <type>' + str(option[0].Value.dwValue) + '</type>\n')
                    f.write('    <url>' + ('' if option[1].Value.pszValue is None else option[1].Value.pszValue) + '</url>\n')
                    f.write('    <proxy>' + ('' if option[2].Value.pszValue is None else option[2].Value.pszValue) + '</proxy>\n')
                    # Parses whether the local addresses are also excluded.
                    bypass = str(option[3].Value.pszValue)
                    local = bypass.find('<local>')
                    f.write('    <bypass local="' + ('1' if local > -1 else '0') + '">' + \
                        (bypass[:local] if local > -1 else '') + '</bypass>\n')
                    f.write('</settings>')
                    f.close()
                except IOError as ex:
                    print '[Error]', ex
            
            # Frees memory
            # Windows 8 raises hangs the script while trying to free the memory from the strings.
            #windll.kernel32.GlobalFree(option[1].Value.pszValue)
            #windll.kernel32.GlobalFree(option[2].Value.pszValue)
            #windll.kernel32.GlobalFree(option[3].Value.pszValue)
            
            return True
        else:
            return False
    
    def change(self, file):
        """Changes the Internet proxy settings according to the given file.
        """
        try:
            # Schema loading.
            print 'Loading Internet Options schema...'
            xsdFile = os.path.dirname(os.path.abspath(__file__)) + '\proxy-settings.xsd'
            xsdDoc = etree.parse(xsdFile)
            schema = etree.XMLSchema(xsdDoc)
            print '[Done]'
            
            # XML parsing and validation.
            config = etree.parse(file)
            print 'Validating Internet Proxy options at [%s]...' % file
            if schema.validate(config):
                print '[Done]'
                
                # Creates the Internet Options structure
                option = {}

                type = config.xpath('/settings/type')
                option[INTERNET_PER_CONN_FLAGS] = int(type[0].text)

                url = config.xpath('/settings/url')
                if len(url) > 0:
                  option[INTERNET_PER_CONN_AUTOCONFIG_URL] = '' if url[0].text is None else str(url[0].text)

                proxy = config.xpath('/settings/proxy')
                if len(proxy) > 0:
                  option[INTERNET_PER_CONN_PROXY_SERVER] = '' if proxy[0].text is None else str(proxy[0].text)

                bypass = config.xpath('/settings/bypass')
                if len(bypass) > 0:
                  bypassStr = '' if bypass[0].text is None else str(bypass[0].text) + ';'
                  # Local addresses to bypass.
                  bypassLocal = config.xpath('/settings/bypass/@local')
                  if int(bypassLocal[0]):
                    bypassStr += '<local>'
                  option[INTERNET_PER_CONN_PROXY_BYPASS] = str(bypassStr)
                
                # Apply changes.
                return self._change(option)
            else:
              print '[Error] The given Internet Proxy options does not comply with the expected schema.'
              print schema.error_log
              return False

        except IOError as ex:
            print '[Error]', ex
            return False
    
    def _change(self, setting):
        """Changes the Internet proxy settings according to the options given in a dict.
        The dict holds as keys the INTERNET_PER_CONN_* constants.
        """
        # Number of settings
        num = len(setting)
        option = (INTERNET_PER_CONN_OPTION * num)()
        # For each setting, it populates the structure.
        for k, v in setting.iteritems():
            num -= 1
            option[num].dwOption = k
            if isinstance(v, int):
                option[num].Value.dwValue = v
            else:
                option[num].Value.pszValue = v
    
        return self.settings.change(option)
      
    
def current(args):
    """Wrapper function to use through argparse to get the current Internet Proxy settings"""
    manager = WindowsProxyManager()
    if not manager.current(args.export):
        sys.exit(1)

def disable(args):
    """Wrapper function to use through argparse to disable the Internet Proxy settings"""
    manager = WindowsProxyManager()
    if not manager.disable():
        sys.exit(1)

def change(args):
    """Wrapper function to use through argparse to change the Internet Proxy settings"""
    manager = WindowsProxyManager()
    if not manager.change(args.file):
        sys.exit(1)
    

    
# Top-level argument parser
parser = argparse.ArgumentParser(description='Manages the Internet Proxy settings')
subparser = parser.add_subparsers(title='sub-commands', help='Available sub-commands')
# Current sub-command
parserCmdCurrent = subparser.add_parser('current', help='Retrieves the current Internet Proxy settings')
parserCmdCurrent.add_argument('-e', '--export', help='File to export current Internet Proxy settings')
parserCmdCurrent.set_defaults(func=current)
# Disable sub-command
parserCmdDisable = subparser.add_parser('disable', help='Disables Internet Proxy settings')
parserCmdDisable.set_defaults(func=disable)
# Change sub-command
parserCmdChange = subparser.add_parser('change', help='Changes Internet Proxy settings')
parserCmdChange.add_argument('-f', '--file', required=True, help='Proxy settings file')
parserCmdChange.set_defaults(func=change)

args = parser.parse_args()
args.func(args)
sys.exit(0)