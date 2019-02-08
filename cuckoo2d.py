from hash_table import HashTable
from linked_list import LinkedList
import math
import random

# Implementation based on https://eprint.iacr.org/2018/120.pdf

class Cuckoo2d:
    def __init__(self, a, b, num_of_keys, prime):
        self.NumOfSlots = int(2*1.2*num_of_keys)
        self.NumOfKeys = num_of_keys
        self.maxKeyBits = int(math.log(2*num_of_keys) / math.log(2) + 1)
        self.Prime = prime
        self.left = 0
        self.right = 1

        self.CuckooTables = [HashTable(a[i], b[i], self.NumOfSlots, self.Prime) for i in range(0, 4)]
        self.CuckooTables.append(LinkedList()) # Stash (only Bob uses)
        self.stash = 4

    # Common method to construct bits using one's own secret part and received part from other party
    def xorSecretAndSharedBits(self, secret, shared):
        xorBitsArray = [ ]
        for i in range(0, 4):
            for j in range(0, self.NumOfSlots):
                k = i*self.NumOfSlots + j
                if secret[k] > -1 and shared[k] > -1: # th evalue of secret/shared can be zero
                    xorBitsArray.append(secret[k] ^ shared[k])
                else:
                    xorBitsArray.append(0)
        return xorBitsArray

    def _getSecretAndSharedBits(self):
        share1 = []
        share2 = []
        for i in range(0, 4):
            for j in range(0, self.NumOfSlots):
                if self.CuckooTables[i].Slot[j].head != None:

                    key = self.CuckooTables[i].Slot[j].head.key
                    # Alice keeps u, Bob shares u
                    randBits = random.getrandbits(self.maxKeyBits)
                    # Alice shares v, Bob keeps v
                    key_xor_randBits = key ^ randBits

                    share1.append(randBits)    # u can be zero
                    share2.append(key_xor_randBits)
                else:
                    share1.append(-1)
                    share2.append(-1)

        return share1, share2

class Alice(Cuckoo2d):
    def __init__(self, a, b, num_of_keys, prime):
        Cuckoo2d.__init__(self, a, b, num_of_keys, prime)
        self.queue = LinkedList()
        self.secretBits = [ ]    # index: k = i*n + j, some of whichTable are set to -1 for empty table slots

    def Insert(self, key, whichTable):
        self.CuckooTables[whichTable].Insert(key)
        self.CuckooTables[whichTable+2].Insert(key)

    def Relocate(self, whichTable):
        for i in range(0, self.NumOfSlots):
            currentElement = self.CuckooTables[whichTable].Slot[i].head
            while currentElement != None and currentElement.next != None:
                self.queue.Insert(currentElement.next.key)
                self.CuckooTables[whichTable].Slot[i].Delete(currentElement.next)

        # delete from other subtable of same side / active table
        currentQueueElement = self.queue.head
        while currentQueueElement != None:
            tableElement = self.CuckooTables[(whichTable+2)%4].Search(currentQueueElement.key)
            self.CuckooTables[(whichTable+2)%4].Delete(tableElement)
            currentQueueElement = currentQueueElement.next

    # Alice's insertion protocol
    def IterativeInsert(self, keySpace, whichTable=0):
        for key in keySpace:
            self.Insert(key, whichTable)

        self.Relocate(whichTable)
        self.Relocate((whichTable+2)%4)

        while self.queue.head != None:  # do something while the relocation pool is nonempty
            whichTable = (whichTable+1) % 2   # change active table

            currentQueueElement = self.queue.head
            while currentQueueElement != None:
                self.Insert(currentQueueElement.key, whichTable) # inserts to both subCuckooTables on one side
                self.queue.Delete(currentQueueElement)
                currentQueueElement = currentQueueElement.next

            self.Relocate(whichTable)
            self.Relocate((whichTable+2)%4)

    # Alice's sharing protocol
    def getSecretAndSharedBits(self):
        self.secretBits, sharedBits = self._getSecretAndSharedBits()
        return sharedBits

class Bob(Cuckoo2d):
    def __init__(self, a, b, num_of_keys, prime):
        Cuckoo2d.__init__(self, a, b, num_of_keys, prime)
        self.maxInsertionTries= 20
        self.secretBits = [ ]
        self.stashBitsArray = []

    # Bob's insertion protocol is based on simple cuckoo hashing
    def Insert(self, key, whichTable):
        num_tries = 0

        hash_key = self.CuckooTables[whichTable].Hash(key)
        currentKey = key
        successfulInsert = False

        while successfulInsert == False:
            if self.CuckooTables[whichTable].Slot[hash_key].head == None:
                LinkedList.Insert(self.CuckooTables[whichTable].Slot[hash_key], currentKey)
                num_tries += 1
                successfulInsert = True
            else:
                LinkedList.Insert(self.CuckooTables[whichTable].Slot[hash_key], currentKey)

                currentElement = self.CuckooTables[whichTable].Slot[hash_key].head.next
                currentKey = currentElement.key

                LinkedList.Delete(self.CuckooTables[whichTable].Slot[hash_key], currentElement)
                whichTable = (whichTable + 2) % 4

                hash_key = self.CuckooTables[whichTable].Hash(currentKey)
                num_tries += 1

            if num_tries > self.maxInsertionTries:
                whichTable = self.stash
                LinkedList.Insert(self.CuckooTables[whichTable], currentKey)
                break

    def InsertAll(self, keySpace):
        for key in keySpace:
            self.Insert(key, self.left)
            self.Insert(key, self.right)

    # Bob's sharing protocol
    def getSecretAndSharedBits(self):
        sharedBits, self.secretBits = self._getSecretAndSharedBits()
        return sharedBits

    # Bob computes the secret/shared bits of the items in his stash
    def getStashSecretAndSharedBits(self):
        stashSharedBits = []

        currentStashElement = self.CuckooTables[self.stash].head
        while currentStashElement != None:
            key = currentStashElement.key
            randBits = random.getrandbits(self.maxKeyBits)
            key_xor_randBits = key ^ randBits

            self.stash.append(key_xor_randBits)
            stash_share.append(randBits)

        return stashSharedBits

    # Bob XOR's his stashed bits with Alice's shared bits
    def xorStashSecretAndSharedBits(self, sharedBitsArray):
        xorBitsArray = [ ]
        if len(self.stashBitsArray) != 0:
            for i in range(0, 4):
                for j in range(0, self.NumOfSlots):
                    k = i*self.NumOfSlots + j

                    for l in range(0, len(self.stashBitsArray)):
                        if sharedBitsArray[k] > 0:
                            xorBitsArray.append(self.stashBitsArray[l] ^ sharedBitsArray[k])
                        else:
                            xorBitsArray.append(0)
        return xorBitsArray
