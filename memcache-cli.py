import cmd
import sys
from memcache import Client

class MemcacheCli(cmd.Cmd, object):

  def __init__(self, host_list):
    super(MemcacheCli, self).__init__()

    self.memcache = Client(host_list)
    self.prompt = '(memcache) '
    for name in dir(self.memcache):
      if not name.startswith('_') and not self._is_hidden(name):
        attr = getattr(self.memcache, name)
        if callable(attr):
          setattr(self.__class__, 'do_' + name, self._make_cmd(name))
          doc = (getattr(attr, '__doc__') or '').strip()
          if doc:  # Not everything has a docstring
            setattr(self.__class__, 'help_' + name, self._make_help(doc))

    # Test for a connection, trying to avoid overwriting existing keys
    if self.memcache.get('a') is None:
      if self.memcache.set('a', 'a') is 0:
        print "\033[91m[Error]\033[0m Unable to connect to memcache"
        sys.exit(1)

  @staticmethod
  def _make_cmd(name):
    def handler(self, line):
        parts = line.split()
        try:
          print getattr(self.memcache, name)(*parts)
        except Exception, e:
          print '\033[91m[Error]\033[0m   ', e
    return handler

  @staticmethod
  def _make_help(doc):
    def help(self):
        print doc
    return help

  @staticmethod
  def _is_hidden(name):
    hidden_commands = 'Error pickler'
    for command in hidden_commands.split():
      if command in name:
        return True
    return False

  def do_exit(self, line):
    return True
  do_EOF = do_exit

  def emptyline(self):
    pass

  
if __name__ == '__main__':
  if len(sys.argv) > 1:
    host_list = sys.argv[1:]
  else:
    print '[Error] No hosts specified'
    sys.exit(1)
  while True:
    try:
      MemcacheCli(host_list).cmdloop()
    except KeyboardInterrupt:
      print "^C"
      continue
    break    
  