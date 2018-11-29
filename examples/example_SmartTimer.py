from smarttimers import SmartTimer

# Create a timing container and print clock info
t = SmartTimer()
t.print_info()

# Measure a block of code
# Sum integers for different powers of 10)
t.tic("outer loop")
sums = []
for pow in range(1, 9):
    t.tic("inner loop")
    sums.append(sum(range(10**pow)))
    t.toc()
t.toc()

# Print times measured in different ways
print(t.times)
print(t.seconds)
print(t.minutes)
print(t.walltime())

# Write times to a file
t.write_to_file(fn="example.txt")
