# memcache-cli
> version 0.1.0

A simple python wrapper for python-memcached to make an easy to use
command line tool.  For now it just provides access to the basic
public runnable commands from the library.  In the future I may add
additional helper commands such as get_hit_rate.

A big thanks to Tyler (@tghw) from FogCreek for posting the Redis
Tutorial that got me started.

http://tghw.com/blog/cheeky-python-a-redis-cli/

Suggestion:

It may be simpler to wrap this with a simple shell script that has
your preferred connection parameters.


## Installing

```console
pip install memcache-cli
```

## Usage:

```console
memcache-cli host1:port host2:port
```

## contributing

### 1. grab the code
```console
git clone https://github.com/andrewgross/memcache-cli.git
cd memcache-cli
pip install -r requirements.pip
```

### 2. hack on it
### 3. send pull requests :)
