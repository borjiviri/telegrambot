import configparser

class Config(object):

    def __init__(self, filename = None, default = None):
        if not filename or not default:
            raise ValueError('filename={0}, default={1}'.
                    format(filename,default))

        cfg = configparser.ConfigParser()
        cfg.optionxform = str

        try:
            cfg.read(filename)
        except FileNotFoundError as e:
            print(e.message)

        for h,v in default.iteritems():
            if not v:
                # Output this whole section as a list of raw key/value tuples
                try:
                    self.__dict__[h] = cfg.items(h)
                except ConfigParser.NoSectionError:
                    self.__dict__[h] = []
            else:
                self.__dict__[h] = config()
                for name, conv, vdefault in v:
                    try:
                        self.__dict__[h].__dict__[name] = conv(cfg.get(h, name))
                    except (ValueError, ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                        self.__dict__[h].__dict__[name] = vdefault

