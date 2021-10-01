from collections.abc import Callable
from collections import ChainMap
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import pickle
from subprocess import Popen
import sys
from tempfile import NamedTemporaryFile
from typing import Optional, Union

@contextmanager
def file_or_tempfile(path: Optional[Union[Path, str]], open_kwargs=None,
ntf_kwargs=None, **kwargs):
  """
  Opens either a new temporary file or the one given by `path` if not `None`.

  The file path can be accessed as a string via its `name` attribute as usual
  or as a `pathlib.Path` object via an added `path` attribute for convenience.
  In either case, it can be relative, so care must be taken to turn it into an
  absolute path if required.

  Also adds an `is_temp` attribute signifying whether a temporary file or the
  file under path was used.

  `**kwargs` go into `open` or `tempfile.NamedTemporaryFile` depending on which
  is called, so you can use arguments common to both as usual. For arguments
  specific to one, use `open_kwargs` or `ntf_kwargs`, which take precedence
  over the common ones.
  """
  if path is not None:
    path = Path(path)
    final_kwargs = ChainMap(open_kwargs or {}, kwargs)
    with path.open(**final_kwargs) as f:
      f.path = path
      f.is_temp = False
      yield f
  else:
    final_kwargs = ChainMap(ntf_kwargs or {}, kwargs)
    with NamedTemporaryFile(**final_kwargs) as ntf:
      ntf.path = Path(ntf.name)
      ntf.is_temp = True
      yield ntf


@dataclass
class PickleFileContents:
  """
  Contents of a pickle file written by PopenFactory: callable and extra data
  """
  callable: Callable
  delete_pickle_file: bool=False


class PopenFactory:
  """
  Returns Popen replacement that loads/executes pickled callable in sub-Python.

  Doesn't do anything special if the child process isn't identified as being a
  Python process.

  The callable is run before any other code in the child Python process.

  Uses the imphook module internally as something that can pre-load code before
  running Python, but doesn't actually use or provide any imphooks.

  Requires this package and its dependencies as well as any modules/packages
  involved in the pickled callable to be importable by the child executable.
  """
  executable_names = ("python", "python2", "python3")

  def __init__(self, callable=None, pickled_path=None):
    """
    Args:
      callable: Callable to be pickled. Must be picklable and loadable from
        within the child Python, obviously. If `None`, will simply act as the
        normal `Popen`.
      pickled_path: File in which to store the pickled data for loading. Will
        be created if it doesn't exist. If `None`, will use a temporary file
        that gets deleted after loading. Otherwise, the file won't be deleted.
        You'll most likely want to set this to something if you ever need to
        inspect the pickled data, as would be typical in automated tests etc.
    """
    self.callable = callable
    self.pickled_path = pickled_path

  def __call__(self, args, **kwargs):
    if not self.subprocess_is_python(args, **kwargs) or self.callable is None:
      # subprocess isn't Python => act as regular Popen
      return Popen(args, **kwargs)
    # subprocess is Python => do our magic
    # write out pickled data
    with file_or_tempfile(self.pickled_path, mode="wb",
      ntf_kwargs=dict(delete=False, suffix=".pickle")
    ) as pickle_file:
      pickle_contents = PickleFileContents(
        callable=self.callable,
        delete_pickle_file=pickle_file.is_temp
      )
      pickle.dump(pickle_contents, pickle_file)
      pickle_path = pickle_file.path.absolute()
    return Popen([args[0], "-m", "imphook", "-i",
      "pickle_spree.imphook_mod", pickle_path, *args[1:]], **kwargs)

  def subprocess_is_python(self, args, **kwargs):
    return (
      args[0] == sys.executable
      or Path(args[0]).name in self.executable_names
    )
