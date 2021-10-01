from collections import ChainMap
import os
from pathlib import Path
from pickle_spree import PopenFactory
import subprocess
import sys

class CallableDefinedInMain:
  def __call__(self):
    return 1

callable = CallableDefinedInMain()

new_popen = PopenFactory(callable=callable)

subprocess.Popen = new_popen

pythonpaths = os.environ.get("PYTHONPATH", "").split(":")
pythonpath = ":".join([str(Path(__file__).parent.absolute())]+pythonpaths)

Path("child_script.py").write_text("print('foo')")

subprocess.run([sys.executable, "child_script.py"],
  env=ChainMap({"PYTHONPATH": pythonpath}, os.environ), check=True)
