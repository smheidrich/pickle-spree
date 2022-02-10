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
  python_requires=">=3",
  setup_requires=[],
  install_requires=[
    "dill>=0.3,<0.4",
    "imphook>=0.5,<0.6",
  ],
  extras_require={
    "tests": [
      "altered-states>=1,<2",
      "pytest>=6,<7",
      "pytest-cov>=2,<3",
      "pytest-datadir>=1,<2",
      "pytest-venv>=0.2,<0.3",
      "codecov>=2,<3",
    ],
  },
)
