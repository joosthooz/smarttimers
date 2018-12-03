.. image:: https://travis-ci.org/edponce/smarttimers.svg?branch=master
   :target: https://travis-ci.org/edponce/smarttimers
   :alt: Tests Status

.. image:: https://codecov.io/gh/edponce/smarttimers/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/edponce/smarttimers
   :alt: Coverage Status

.. image:: https://readthedocs.org/projects/smarttimers/badge/?version=latest
   :target: https://smarttimers.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/edponce/smarttimers/blob/master/LICENSE

|

SmartTimers
===========

SmartTimers is a collection of libraries for measuring runtime of running
processes using a simple and flexible API. Time can be measured in sequential
and nested code blocks.

A SmartTimer allows recording elapsed time in an arbitrary
number of code blocks. Specified points in the code are marked as either
the beginning of a block to measure, ``tic``, or as the end of a
measured block, ``toc``. Times are managed internally and ordered
based on ``tic`` calls. Times can be queried, operated on, and
written to file.

The following schemes are supported for timing code blocks
    * Consecutive: ``tic('A')``, ``toc()``, ..., ``tic('B')``, ``toc()``
    * Cascade: ``tic('A')``, ``toc()``, ``toc()``, ...
    * Nested: ``tic('A')``, ``tic('B')``, ..., ``toc()``, ``toc()``
    * Label-paired: ``tic('A')``, ``tic('B')``, ..., ``toc('A')``,
      ``toc('B')``
    * Mixed: arbitrary combinations of schemes

.. literalinclude:: examples/example_SmartTimer.py
    :language: python
    :linenos:
    :caption: SmartTimer API examples.

.. literalinclude:: examples/example.txt
    :language: text
    :caption: Sample output file (*example.txt*).
