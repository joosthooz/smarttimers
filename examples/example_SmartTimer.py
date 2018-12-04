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

# Write times to file 'Example.txt'
t.to_file()

print(t.times)
print(t["info"])
print(t.walltime())
print(t)

# Print stats only for labels with keyword 'iter'
print(t.stats("iter"))
