"""ROSE's logging, replacing the per-module `if CLASS_DEBUG: print(...)` flags.

Self-contained on purpose - no stdlib logging, so nothing here can be disturbed
by, or disturb, Maya's own logging configuration. Output goes through print() so
it lands in the Script Editor like it always has.

Usage, one line per module:

    log = ROSE_Log.get("rose.components.guides")
    log.debug("--guideBuild:: building", self.name)

The rule: debug() and info() only emit while their channel is switched on in
preferences. warning() and error() always emit - they report things the user
needs to see, and were the reason ~200 print() calls could not simply be deleted.

For anything more expensive than passing a few values - a loop, or building a
string that isn't needed otherwise - guard it, because arguments are evaluated
before the call regardless:

    if log.enabled:
        for guide in self.guides:
            log.debug("\t", guide)
"""

LEVEL_DEBUG = "DEBUG"
LEVEL_INFO = "INFO"
LEVEL_WARNING = "WARNING"
LEVEL_ERROR = "ERROR"

class ROSE_Log:

    _loggers = {}
    _enabled_channels = set()
    #bumped whenever the enabled set changes, so each logger knows to re-resolve
    #its cached answer instead of walking the dotted name on every call
    _generation = 0

    def __init__(self, channel):
        self.channel = channel
        self._cached_enabled = False
        self._cached_generation = -1

    @classmethod
    def get(cls, channel):
        if channel not in cls._loggers:
            cls._loggers[channel] = cls(channel)
        return cls._loggers[channel]

# Channel state

    @classmethod
    def isChannelEnabled(cls, channel):
        #a channel is on if it, or any of its ancestors, is on - switching on
        #"rose.skinning" covers "rose.skinning.deform_list" and the rest
        if not cls._enabled_channels:
            return False

        name_parts = channel.split(".")
        for depth in range(len(name_parts), 0, -1):
            if ".".join(name_parts[:depth]) in cls._enabled_channels:
                return True
        return False

    @classmethod
    def setChannelEnabled(cls, channel, is_enabled):
        if is_enabled:
            cls._enabled_channels.add(channel)
        else:
            cls._enabled_channels.discard(channel)
        cls._generation += 1

    @classmethod
    def setEnabledChannels(cls, channels):
        cls._enabled_channels = set(channels)
        cls._generation += 1

    @classmethod
    def getEnabledChannels(cls):
        return sorted(cls._enabled_channels)

    @classmethod
    def disableAll(cls):
        cls.setEnabledChannels([])

    @property
    def enabled(self):
        if self._cached_generation != ROSE_Log._generation:
            self._cached_enabled = ROSE_Log.isChannelEnabled(self.channel)
            self._cached_generation = ROSE_Log._generation
        return self._cached_enabled

# Writing

    def debug(self, *message_parts):
        if self.enabled:
            self.write(LEVEL_DEBUG, message_parts)

    def info(self, *message_parts):
        if self.enabled:
            self.write(LEVEL_INFO, message_parts)

    def warning(self, *message_parts):
        self.write(LEVEL_WARNING, message_parts)

    def error(self, *message_parts):
        self.write(LEVEL_ERROR, message_parts)

    def write(self, level, message_parts):
        #joined the way print() would, so migrated call sites keep reading the
        #same way they did as print(a, b, c)
        message = " ".join(str(part) for part in message_parts)
        print("[ROSE %s][%s] %s" % (level, self.channel, message))

    def __str__(self):
        return "ROSE_Log(%s)" % self.channel
