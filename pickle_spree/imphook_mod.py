"""
Module to be run via imphook that loads and calls the pickled cb at argv[0]
"""
from os import unlink
from pickle import load
from sys import argv
pickle_path = argv.pop(0)
with open(pickle_path, "rb") as f:
  contents = load(f)
if contents.delete_pickle_file:
  unlink(pickle_path)
contents.callable()
