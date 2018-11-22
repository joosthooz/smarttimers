from smarttimer import Timer

# Find the current time function of a Timer
t1 = Timer('Timer1')
print(Timer.CLOCKS[t1.clock_name])
# or
Timer.print_clocks()
print(t1.clock_name)

# Change current time function
t1.clock_name = 'process_time'

# Record a time measurement
t1.time()
print(t1)

# Create another Timer compatible with 'Timer1'
t2 = Timer('Timer2', clock_name='process_time')
t2.print_info()
t2.time()
print(t2)

# Sum Timers
t3 = Timer.sum(t1, t2)
# or
t3 = t1 + t2
print(t3)

# Find difference between Timers
t4 = Timer.diff(t1, t2)
# or
t4 = t2 - t1
print(t4)

# Compare Timers
print(t1 == t2)  # False
print(t2 > t1)   # True
print(t4 <= t3)  # True
