# pickle-spree

[![pipeline status](https://gitlab.com/smheidrich/pickle-spree/badges/main/pipeline.svg?style=flat-square)](https://gitlab.com/smheidrich/pickle-spree/-/commits/main)
[![codecov](https://img.shields.io/codecov/c/gl/smheidrich/pickle-spree?style=flat-square&token=OIHAYW5MD8)](https://codecov.io/gl/smheidrich/pickle-spree)

**Pre-load and run pickled callables in Python subprocesses**


## What does this do?

It provides a class `PopenFactory` whose instances constitute replacements for
[`subprocess.Popen`][popen]<sup>1</sup> which check if the process to be
executed is a Python process; if so, it [pickles][pickle]<sup>2</sup> a given
callable, then loads and runs it inside the child Python before any other code
is executed in it.

<sup>1</sup> And other parts of `subprocess` that use `Popen` internally, such
as [`run`][run].

<sup>2</sup> Actually [dilled][dill] to handle some [edge cases][GH1] better.


## Why would I need this?

The use case this was written for is convenient monkeypatching within a child
Python process, e.g. to patch in mocks for testing when the tested library
itself spawns Python subprocesses as part of its operation.


## Example

Here is an [example][example_py] that monkeypatches `sys.stdout` in a Python
subprocess so that printed messages are redirected to a file:

```python
from pickle_spree import PopenFactory

from pathlib import Path
import subprocess
import sys

class SysStdoutRedirectingPatch:
  """
  Callable that patches sys.stdout to redirect writes to the given file
  """
  def __init__(self, redirect_to):
    self.redirect_to = redirect_to

  def __call__(self):
    def redirected_write(s):
      with open(self.redirect_to, "a") as f:
        f.write(s)
    import sys
    sys.stdout.write = redirected_write

patch = SysStdoutRedirectingPatch("output.txt")
Path("output.txt").unlink(missing_ok=True) # delete previous output file

# construct Popen replacement and tell it which callable to pickle for loading
# and execution in the Python subprocess
new_popen = PopenFactory(callable=patch, pickled_path="dbg.pickle")

# manually monkeypatch subprocess.Popen; for greater convenience, you could use
# a library like https://github.com/Plexical/altered.states
old_popen = subprocess.Popen
subprocess.Popen = new_popen

if __name__ == "__main__":
  # write script to run in child Python subprocess
  Path("child_script.py").write_text("print('Hello world')")

  # run subprocess using the same executable as the current Python process
  # (usually guarantees being able to load pickled data)
  subprocess.run([sys.executable, "child_script.py"], check=True)

  # check whether everything worked and output was actually redirected:
  output_from_file = Path("output.txt").read_text()
  print(f"output found in output.txt: {output_from_file}") # 'Hello world'

# undo monkeypatching (again, better use something like altered-states)
subprocess.Popen = old_popen
```


## Installation

```bash
pip install git+https://gitlab.com/smheidrich/pickle-spree.git
```


## API

As the code is extremely short, just have a look at the docstrings
[there][init_py].


## Limitations

- Callables must obviously be picklable (but as we use dill, the requirements
  are a bit more lax, see [here][dill_features]) and the pickled data must be
  loadable by the child Python interpreter.
- Normally, the 2nd requirement entails that all modules defining classes,
  functions etc. which are used inside the pickled data are importable.
  However, we use *dill* instead of *pickle*, which writes any definitions it
  encounters within the "main" script into the pickle file (TODO: what about
  other modules?), so you don't have to do anything to ensure that this one can
  be imported, which would be the trickiest bit. It's enough to ensure that any
  modules the main script itself imports can be imported by the child Python
  interpreter.
- The full range of command-line arguments for child Python interpreters is not
  available. Only those supported by [imphook], which are `-m module` and
  `name_of_your_script.py`, will work. Sorry about that, could be fixed in
  theory but I don't need it right now.


## Related projects

- [pymonkey] (inactive): Also meant to allow pre-patching in Python processes,
  but doesn't do any automatic pickling. In principle, pymonkey could be used
  as a "backend" for pickle-spree that takes care of the pre-execution, but I
  currently (ab)use [imphook] for that as I find it easier to understand.


[popen]: https://docs.python.org/3/library/subprocess.html#subprocess.Popen
[run]: https://docs.python.org/3/library/subprocess.html#subprocess.run
[pickle]: https://docs.python.org/3/library/pickle.html
[dill]: https://dill.readthedocs.io/en/latest/
[GH1]: https://gitlab.com/smheidrich/pickle-spree/-/issues/1
[example_py]: https://gitlab.com/smheidrich/pickle-spree/-/blob/main/pickle_spree/__example__.py
[init_py]: https://gitlab.com/smheidrich/pickle-spree/-/blob/main/pickle_spree/__init__.py
[dill_features]: https://dill.readthedocs.io/en/latest/#major-features
[imphook]: https://github.com/pfalcon/python-imphook
[pymonkey]: https://github.com/asottile-archive/pymonkey
