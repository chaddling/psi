import cuckoo2d

# To do:
# 1. get rid of the p initialization while calling, initialize each of A and B's hash subtable
#    with same p
# 2. use better quality hash function

# quick check using simple intersection
def intersection(A, B):
    I = [v for v in A if v in B]
    return I

# quick check - make sure hashing is done correctly
def PSI_check(A, B):
    I = []

    for i in range(0, 4):
        for j in range(0, A.NumOfSlots):
            x = A.CuckooTables[i].Slot[j].head
            y = B.CuckooTables[i].Slot[j].head
            if x != None and y != None and not x.key ^ y.key: # direct comparison of hashed elements
                I.append(x.key)

    # compare Bob's stash to all of Alice's items
    x = B.CuckooTables[4].head
    while x != None:
        for i in [0, 1]:
            y = A.CuckooTables[i].Search(x.key)
            z = B.CuckooTables[i].Search(x.key)
            if y != None and z == None and not x.key ^ y.key:
                I.append(y.key)
        x = x.next

    return I

# proof of concept: comparison using GMW protocol without passing actual info into function evaluation
# GMW protocol: https://dl.acm.org/citation.cfm?id=28420
def PSI(A_bits, B_bits, stash_bits, n):
    I = []
    for i in range(0, 4):
        for j in range(0, n):
            k = i*n + j

            if A_bits[k] and B_bits[k]:
                compare = A_bits[k] ^ B_bits[k]
                if not compare:
                    I.append([i, j]) # return the (i, j) pair for look up
            elif A_bits[k] > 0:
                for l in range(0, len(stash)):
                    compare2 = A_bits[k] ^ stash_bits[l] # compares Alice's bits with Bob's stash
                    if not compare2:
                        I.append([i, j])
    return I

# use this to check that PSI() correctly outputs ind pairs and compare results to intersection(A, B)
def lookup(A, ind):
    I = []
    for i in ind:
        I.append(A.CuckooTables[i[0]].Slot[i[1]].head.key)
    return I
