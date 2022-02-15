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
    * Series: ``tic('A')``, ``toc()``, ..., ``tic('B')``, ``toc()``
    * Cascade: ``tic('A')``, ``toc()``, ``toc()``, ...
    * Nested: ``tic('A')``, ``tic('B')``, ..., ``toc()``, ``toc()``
    * Label-paired: ``tic('A')``, ``tic('B')``, ..., ``toc('A')``,
      ``toc('B')``
    * Mixed: arbitrary combinations of schemes

.. code:: python

    from smarttimers import SmartTimer

    # Create a timer instance named 'Example'
    t = SmartTimer("Example")

    # Print clock details
    t.tic("info")
    t.print_info()
    t.toc()

    # Measure iterations in a loop
    t.tic("loop")
    for i in range(10):
        t.tic("iter " + str(i))
        sum(range(1000000))
        t.toc()
    t.toc()

    t.tic("sleep")
    t.sleep(2)
    t.toc()

    # Write times to file 'Example-times.csv'
    t.dump_times()

    print(t["info"])
    print(t.walltime)

.. code:: python

    # Print times measured in different ways
    >>> print(t)
     label,  seconds,  minutes, rel_percent, cumul_sec, cumul_min,cumul_percent
      info, 0.000270, 0.000004,      0.0001,  0.000270,  0.000004,       0.0001
      loop, 0.153422, 0.002557,      0.0664,  0.153692,  0.002562,       0.0666
    iter 0, 0.022840, 0.000381,      0.0099,  0.176531,  0.002942,       0.0765
    iter 1, 0.023248, 0.000387,      0.0101,  0.199780,  0.003330,       0.0865
    iter 2, 0.017198, 0.000287,      0.0074,  0.216977,  0.003616,       0.0940
    iter 3, 0.012921, 0.000215,      0.0056,  0.229898,  0.003832,       0.0996
    iter 4, 0.012754, 0.000213,      0.0055,  0.242652,  0.004044,       0.1051
    iter 5, 0.012867, 0.000214,      0.0056,  0.255519,  0.004259,       0.1107
    iter 6, 0.012843, 0.000214,      0.0056,  0.268361,  0.004473,       0.1162
    iter 7, 0.012789, 0.000213,      0.0055,  0.281150,  0.004686,       0.1218
    iter 8, 0.012818, 0.000214,      0.0056,  0.293969,  0.004899,       0.1273
    iter 9, 0.012856, 0.000214,      0.0056,  0.306825,  0.005114,       0.1329
     sleep, 2.002152, 0.033369,      0.8671,  2.308977,  0.038483,       1.0000

    # Print stats only for labels with keyword 'iter'
    >>> print(t.stats("iter"))
    namespace(avg=(0.015313280202099122, 0.00025522133670165205),
    max=(0.023248409008374438, 0.0003874734834729073),
    min=(0.012753532995702699, 0.00021255888326171163),
    total=(0.15313280202099122, 0.0025522133670165203))
