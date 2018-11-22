"""Unit tests for SmartTimer module.

Note:
    These are approaches for tests that have side effects on class variables:
        * Save and restore class variables at the beginning/end of each method.
        * Change class names that modify class variables so that they are run
          last (ordering is alphabetically: class name -> method name).
"""
