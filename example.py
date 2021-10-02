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

if __name__ == "__main__":
  patch = SysStdoutRedirectingPatch("output.txt")
  Path("output.txt").unlink(missing_ok=True) # delete previous output file

  # construct Popen replacement and tell it which callable to pickle for
  # loading and execution in the Python subprocess
  new_popen = PopenFactory(callable=patch, pickled_path="dbg.pickle")

  # manually monkeypatch subprocess.Popen; for greater convenience, you could
  # use a library like https://github.com/Plexical/altered.states
  old_popen = subprocess.Popen
  subprocess.Popen = new_popen

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
