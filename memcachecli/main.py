# #!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <andrew.w.gross@gmail.com> wrote this file. As long as you retain
# this notice you can do whatever you want with this stuff. If we meet
# some day, and you think this stuff is worth it, you can buy me a
# beer in return Poul-Henning Kamp
# ----------------------------------------------------------------------------

import cmd
import sys
from memcache import Client
import pprint

# This coloring won't work on windows, womp womp
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
    self.memcache = Client(host_list) # Use our memcache library to initiate a connection
    self._check_connection(host_list) # Make sure we actually have connections, since our library doesn't make this apparent
    self.prompt = '(memcache) '
    # Time for some hardcore introspection and dynamic method creation
    for name in dir(self.memcache):
      # List our methods, ignoring private methods and ones that should be hidden to our CLI
      if not name.startswith('_') and not self._is_hidden(name):
        attr = getattr(self.memcache, name)
        if callable(attr):
          # Make sure we only keep callable methods, let's pin the doc strings to them while we are at it
          setattr(self.__class__, 'do_' + name, self._make_cmd(name))
          doc = (getattr(attr, '__doc__') or '').strip()
          if doc:  # Not everything has a docstring
            setattr(self.__class__, 'help_' + name, self._make_help(doc))

  @staticmethod
  def _make_cmd(name):
    # Whats a little functional passing between friends?
    # This is our core factory for creating dynamic methods
    def _get_stats(self, line):
      try:
        pp = pprint.PrettyPrinter(depth=4)
        pp.pprint(self.memcache.get_stats(line))
      except Exception, e:
        print_error(e)

    def handler(self, line):
        parts = line.split()
        try:
          # This is where the magic happens, get our function by name, pass the arguments, then pretty-print the results
          pprint.pprint(getattr(self.memcache, name)(*parts))
        except Exception, e:
          print_error(e)
    # Because get_stats doesn't take *args, but a string
    if 'get_stats' in name:
      return _get_stats
    return handler

  @staticmethod
  # This just lets cmd know how to print help commands for arbitrary methods
  def _make_help(doc):
    def help(self):
        print doc
    return help

  def _check_connection(self, host_list):
    # Get Stats for all hosts, make sure we connect to all of them
    unreachable_hosts = []
    reachable_hosts = []
    stats = self.memcache.get_stats()
    # Stats returns a list with each host getting a tuple with two elements, a string and a dictionary (We just hit 3 of the python data structures in one return, wtf)
    # The string contains the hostname and some other junk
    # The dictionary contains all of the stats for that host
    for stat in stats:
      reachable_hosts.append(stat[0].split()[0])
    # Compare our list of reachable hosts with the ones we were passed
    unreachable_hosts = [ host for host in host_list if host not in reachable_hosts ]
    if unreachable_hosts:
      for host in unreachable_hosts:
        print_error("Unable to connect to memcache server: %s" % host)
      sys.exit(1)

  # Helper method for trimming out arbitrary commands from our library
  def _is_hidden(self, name):
    hidden_commands = ['Error', 'pickler']
    for command in hidden_commands:
      if command in name:
        return True
    return False

  # Custom Command not in the library
  def do_get_hit_rate(self, line):
    try:
      stats = self.memcache.get_stats()
      total_hits = 0
      total_misses = 0
      total_calls = 0
      hit_rate = 0
      hit_percentage = 0
      for machine in stats:
        for k,v in machine[1].items():
          if 'misses' in k and 'get' in k:
            total_misses = total_misses + int(v)
          if 'hits' in k and 'get' in k:
            total_hits = total_hits + int(v)
      total_calls = total_hits + total_misses
      hit_rate = float(total_hits)/total_calls
      print hit_rate
    except Exception, e:
      print_error(e)

  # Make it so we can exit easily
  def do_exit(self, line):
    return True
  do_EOF = do_exit

  # We don't want to repeat the last command if a blank line is entered, so we pass
  def emptyline(self):
    pass


def main():
    # parse our inputs, which should be memcache server host:port strings
    if len(sys.argv) > 1:
        host_list = sys.argv[1:]
    else:
        host_list = ['localhost:11211']
        print_warning('No hosts specified, defaulting to %s' % host_list[0])
    # Some banner fun to make our CLI all warm and fuzzy
    print "Connecting to %s" % (', '.join(host_list))
    # Outer loop so we can recover from interrupts, which cmd does not
    # handle well
    while True:
        try:
            # Inner loop which actually runs the CMD
            MemcacheCli(host_list).cmdloop()
        except KeyboardInterrupt:
            print "^C"
            continue
        break


if __name__ == '__main__':
    main()
