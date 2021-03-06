"""
Misc. useful functions that can be used at many places in the program.
"""

import subprocess as sp
import sys
import warnings
import re

import os
from .compat import DEVNULL


def sys_write_flush(s):
    """ Writes and flushes without delay a text in the console """
    sys.stdout.write(s)
    sys.stdout.flush()


def verbose_print(verbose, s):
    """ Only prints s (with sys_write_flush) if verbose is True."""
    if verbose:
        sys_write_flush(s)


def subprocess_call(cmd, verbose=True, errorprint=True):
    """ Executes the given subprocess command."""

    verbose_print(verbose, "\n[MoviePy] Running:\n>>> "+ " ".join(cmd))

    popen_params = {"stdout": DEVNULL,
                    "stderr": sp.PIPE,
                    "stdin": DEVNULL}

    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000

    proc = sp.Popen(cmd, **popen_params)

    out, err = proc.communicate() # proc.wait()
    proc.stderr.close()

    if proc.returncode:
        verbose_print(errorprint, "\n[MoviePy] This command returned an error !")
        raise IOError(err.decode('utf8'))
    else:
        verbose_print(verbose, "\n... command successful.\n")

    del proc

def is_string(obj):
    """ Returns true if s is string or string-like object,
    compatible with Python 2 and Python 3."""
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str)

def cvsecs(time):
    """ Will convert any time into seconds.
    Here are the accepted formats:

    >>> cvsecs(15.4) -> 15.4 # seconds
    >>> cvsecs( (1,21.5) ) -> 81.5 # (min,sec)
    >>> cvsecs( (1,1,2) ) -> 3662 # (hr, min, sec)
    >>> cvsecs('01:01:33.5') -> 3693.5  #(hr,min,sec)
    >>> cvsecs('01:01:33.045') -> 3693.045
    >>> cvsecs('01:01:33,5') #coma works too
    """

    if is_string(time):
        if (',' not in time) and ('.' not in time):
            time = time + '.0'
        expr = r"(\d+):(\d+):(\d+)[,|.](\d+)"
        finds = re.findall(expr, time)[0]
        nums = list( map(float, finds) )
        return ( 3600*int(finds[0])
                + 60*int(finds[1])
                + int(finds[2])
                + nums[3]/(10**len(finds[3])))

    elif isinstance(time, tuple):
        if len(time)== 3:
            hr, mn, sec = time
        elif len(time)== 2:
            hr, mn, sec = 0, time[0], time[1]
        return 3600*hr + 60*mn + sec

    else:
        return time

def deprecated_version_of(f, oldname, newname=None):
    """ Indicates that a function is deprecated and has a new name.

    `f` is the new function, `oldname` the name of the deprecated
    function, `newname` the name of `f`, which can be automatically
    found.

    Returns
    ========

    f_deprecated
      A function that does the same thing as f, but with a docstring
      and a printed message on call which say that the function is
      deprecated and that you should use f instead.

    Examples
    =========

    >>> # The badly named method 'to_file' is replaced by 'write_file'
    >>> class Clip:
    >>>    def write_file(self, some args):
    >>>        # blablabla
    >>>
    >>> Clip.to_file = deprecated_version_of(Clip.write_file, 'to_file')
    """

    if newname is None: newname = f.__name__

    warning= ("The function ``%s`` is deprecated and is kept temporarily "
              "for backwards compatibility.\nPlease use the new name, "
              "``%s``, instead.")%(oldname, newname)

    def fdepr(*a, **kw):
        warnings.warn("MoviePy: " + warning, PendingDeprecationWarning)
        return f(*a, **kw)
    fdepr.__doc__ = warning

    return fdepr


# non-exhaustive dictionnary to store default informations.
# any addition is most welcome.
# Note that 'gif' is complicated to place. From a VideoFileClip point of view,
# it is a video, but from a HTML5 point of view, it is an image.

extensions_dict = { "mp4":  {'type':'video', 'codec':['libx264','libmpeg4']},
                    'ogv':  {'type':'video', 'codec':['libtheora']},
                    'webm': {'type':'video', 'codec':['libvpx']},
                    'avi':  {'type':'video'},
                    'mov':  {'type':'video'},

                    'ogg':  {'type':'audio', 'codec':['libvorbis']},
                    'mp3':  {'type':'audio', 'codec':['libmp3lame']},
                    'wav':  {'type':'audio', 'codec':['pcm_s16le', 'pcm_s32le']},
                    'm4a':  {'type':'audio', 'codec':['libfdk_aac']}
                  }

for ext in ["jpg", "jpeg", "png", "bmp", "tiff"]:
    extensions_dict[ext] = {'type':'image'}

def find_extension(codec):
    for ext,infos in extensions_dict.items():
        if ('codec' in infos) and codec in infos['codec']:
            return ext
    raise ValueError
