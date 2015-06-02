from  ConfigParser import RawConfigParser


class CConfig(RawConfigParser):

    def __init__(self):
        RawConfigParser.__init__(self)
        
    def get(self, section, option, default=''):
        if self.has_option(section, option):
            return RawConfigParser.get(self, section, option)
        else:
            return default
    
    def getFloat(self, section, option, default=0.0):
        if self.has_option(section, option):
            return RawConfigParser.getfloat(self, section, option)
        else:
            return default
        
    def getInt(self, section, option, default=0):
        if self.has_option(section, option):
            return RawConfigParser.getint(self, section, option)
        else:
            return default
    def getBoolean(self, section, option, default=False):
        if self.has_option(section, option):
            return RawConfigParser.getboolean(self, section, option)
        else:
            return default

if __name__ == '__main__':
    
    config = CConfig()
    config.read('log_server.ini')
    print config.get('sys', 'udp_ip', 'localhost')
    print config.getInt('sys', 'port1', 100)
    
