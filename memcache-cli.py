import cmd
import sys
from memcache import Client

def print_error(message):
  RED='\033[91m'
  END='\033[0m'
  print '%s[ERROR]%s %s' % (RED, END, message)

def print_warning(message):
  YELLOW='\033[33m'
  END='\033[0m'
  print '%s[WARNING]%s %s' % (YELLOW, END, message)

class MemcacheCli(cmd.Cmd, object):

  def __init__(self, host_list):
    super(MemcacheCli, self).__init__()
    self.memcache = Client(host_list)
    self._check_connection(host_list)
    self.prompt = '(memcache) '
    for name in dir(self.memcache):
      if not name.startswith('_') and not self._is_hidden(name):
        attr = getattr(self.memcache, name)
        if callable(attr):
          setattr(self.__class__, 'do_' + name, self._make_cmd(name))
          doc = (getattr(attr, '__doc__') or '').strip()
          if doc:  # Not everything has a docstring
            setattr(self.__class__, 'help_' + name, self._make_help(doc))

  @staticmethod
  def _make_cmd(name):
    def handler(self, line):
        parts = line.split()
        try:
          print getattr(self.memcache, name)(*parts)
        except Exception, e:
          print_error(e)
    return handler

  @staticmethod
  def _make_help(doc):
    def help(self):
        print doc
    return help

  def _check_connection(self, host_list):
    # Get Stats for all hosts, make sure we connect to all of them
    unreachable_hosts = []
    reachable_hosts = []
    stats = self.memcache.get_stats()
    for stat in stats:
      reachable_hosts.append(stat[0].split()[0])
    unreachable_hosts = [ host for host in host_list if host not in reachable_hosts ]
    if unreachable_hosts:
      for host in unreachable_hosts:
        print_error("Unable to connect to memcache server: %s" % host)
      sys.exit(1)


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
    host_list = ['localhost:11211']
    print_warning('No hosts specified, using %s' % host_list[0])
  print "Connecting to %s" % (', '.join(host_list))
  while True:
    try:
      MemcacheCli(host_list).cmdloop()
    except KeyboardInterrupt:
      print "^C"
      continue
    break    


  