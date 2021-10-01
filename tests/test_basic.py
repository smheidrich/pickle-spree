"""
Tests for basic functionality
"""
from altered import state
from collections import ChainMap
import os
from pathlib import Path
from pickle_spree import PopenFactory
import pytest
import subprocess as sp
import sys

class SysStdoutRedirectingCallable:
  def __init__(self, redirect_to: Path):
    self.redirect_to = redirect_to

  def __call__(self):
    def redirected_write(s):
      with open(self.redirect_to, "a") as f:
        f.write(s)
    import sys
    sys.stdout.write = redirected_write


@pytest.mark.parametrize("explicit_pickle_file", [True,False])
def test_basic_with_same_executable(tmp_path, explicit_pickle_file):
  for_python_executable(executable=sys.executable, tmp_path=tmp_path,
    explicit_pickle_file=explicit_pickle_file)


def test_basic_with_venv_executable(venv, tmp_path):
  # install required pkgs into venv
  # TODO don't rely on cwd being at package root
  venv.install(".[tests]")
  for_python_executable(executable=venv.python, tmp_path=tmp_path)


def for_python_executable(executable, tmp_path, explicit_pickle_file=False):
  """
  Check that basic functionality works for a given Python executable

  Factored out from the two tests above.
  """
  if explicit_pickle_file:
    pickled_path = tmp_path/"pickle_spree.pickle"
  else:
    pickled_path = None
  output_path = tmp_path/"output"
  callable = SysStdoutRedirectingCallable(output_path)
  new_popen = PopenFactory(callable=callable, pickled_path=pickled_path)
  # need to add our directory to PYTHONPATH as test modules aren't globally
  # discoverable with our project layout (tests outside of package)
  pythonpaths = os.environ.get("PYTHONPATH", "").split(":")
  pythonpath = ":".join([str(Path(__file__).parent.absolute())]+pythonpaths)
  # write out main module
  main_module_path = tmp_path/"main_module.py"
  main_module_path.write_text("print('foo')")
  # run main module as subprocess
  with state(sp, Popen=new_popen):
    sp.run([sys.executable, main_module_path],
      env=ChainMap({"PYTHONPATH": pythonpath}, os.environ), check=True)
  assert output_path.read_text() == "foo\n"
  if explicit_pickle_file:
    assert pickled_path.exists()
  else:
    assert not (tmp_path/"pickle_spree.pickle").exists()
