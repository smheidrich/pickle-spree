from pickle_spree import PopenFactory

from collections import ChainMap
import os
from pathlib import Path
import subprocess
import sys

class SysStdoutRedirectingCallable:
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

callable = SysStdoutRedirectingCallable("output.txt")

# construct Popen replacement and tell it which callable to pickle for loading
# and execution in the Python subprocess
new_popen = PopenFactory(callable=callable, pickled_path="dbg.pickle")

# manually monkeypatch subprocess.Popen; for greater convenience, you could use
# a library like https://github.com/Plexical/altered.states
old_popen = subprocess.Popen
subprocess.Popen = new_popen

# need to add our directory to PYTHONPATH as our script is not necessarily
# importable, e.g. if run from a different directory (this wouldn't be
# necessary if our code was part of a package meant to be installed):
pythonpaths = os.environ.get("PYTHONPATH", "").split(":")
pythonpath = ":".join([str(Path(__file__).parent.absolute())]+pythonpaths)

# write "main" script to run in Python subprocess
Path("main_script.py").write_text("print('Hello world')")

# run subprocess using the same executable as the current Python process
# (usually guarantees being able to load pickled data)
subprocess.run([sys.executable, "main_script.py"],
  env=ChainMap({"PYTHONPATH": pythonpath}, os.environ), check=True)

# check if everything worked and output was actually redirected:
output_from_file = Path("output.txt").read_text()
print(f"output found in output.txt: {output_from_file}") # 'Hello world'
