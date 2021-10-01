"""
Regression test for bug that occurs when pickling things defined in __main__

See: https://gitlab.com/smheidrich/pickle-spree/-/issues/1
"""
from subprocess import run
import sys

def test_pickling_things_defined_in_main(tmp_path, datadir):
  run([sys.executable, datadir/"main.py"], cwd=tmp_path, check=True)
