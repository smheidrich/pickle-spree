from setuptools import setup

setup(
  name="pickle-spree",
  version="0.1",
  description="Pre-load and run pickled callables in Python subprocesses",
  keywords="",
  url="",
  author="Shahriar Heidrich",
  author_email="smheidrich@weltenfunktion.de",
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3.9",
  ],
  packages=["pickle_spree"],
  setup_requires=[],
  install_requires=[
    "dill",
    "imphook",
  ],
  extras_require={
    "tests": [
      "altered-states",
      "pytest",
      "pytest-cov",
      "pytest-datadir",
      "pytest-venv",
      "codecov",
      "sybil",
    ],
  },
)
