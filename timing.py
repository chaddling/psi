import libpsi as lpsi
import cuckoo2d as c2d
import random
import numpy as np
import time

# Time the runtime of different intersection routines in libpsi.py
# (excluding pre-computation time)

m = 100000
n = int(2*1.2*m)
p = 200023 # pick prime > 2m, but close to m in order of magnitude?
a = [random.randint(1, p-1) for i in range(0, 4)]
b = [random.randint(0, p-1) for i in range(0, 4)]

sample = [(i+1) for i in range(0, 2*m)]

A = np.random.choice(sample, size=m, replace=False)
B = np.random.choice(sample, size=m, replace=False)

t1 = time.time()
C = lpsi.intersection(A, B)
t2 = time.time()
C.sort()

print("Size of intersection of sets A and B:", len(C))
print("Execution time = ", t2 - t1)

# Checking 2D Cuckoo hashing gives correct results

Alice = c2d.Alice(a, b, m, p)
Alice.IterativeInsert(A)

Bob = c2d.Bob(a, b, m, p)
Bob.InsertAll(B)

t1 = time.time()
D = lpsi.PSI_check(Alice, Bob)
t2 = time.time()
D.sort()

print("Size of intersection of sets A and B (check):", len(D))
print("Execution time = ", t2 - t1)
print("2D Cuckoo hashing on A, B gives same result as intersection(A, B): ", C == D)

# Pre-computation for PSI using GMW protocol
# Compute partial bits shared to the other party
# As well as the partial secret bits that one keeps
bitsSharedToBob = Alice.getSecretAndSharedBits()
bitsSharedToAlice = Bob.getSecretAndSharedBits()
# this can return the partial bits of Bob's stash, but we omit it
Bob.getStashSecretAndSharedBits()

# XOR of secret + shared bits by both parties
Alice_bits = Alice.xorSecretAndSharedBits(Alice.secretBits, bitsSharedToAlice)
Bob_bits = Bob.xorSecretAndSharedBits(Bob.secretBits, bitsSharedToBob)
# XOR of secret bits of Bob's stash + Alice's shared bits
Stash_bits = Bob.xorStashSecretAndSharedBits(bitsSharedToBob)

t1 = time.time()
# PSI() only operates on the reconstructed bits by both parties
E = lpsi.PSI(Alice_bits, Bob_bits, Stash_bits, n)
t2 = time.time()

F = lpsi.lookup(Alice, E)
F.sort()

print("Size of intersection of sets A and B (using GMW protocol to evaluate PSI): ", len(E))
print("Execution time = ", t2 - t1)
print("PSI protocol on A, B gives same result as intersection(A, B): ", C == F)
