# Implementation of basic cuckoo hashing
from hash_table import HashTable
from linked_list import LinkedList
import random

class Cuckoo:
    def __init__(self, a, b, num_of_keys, prime):
        self.NumOfSlots = int(1.2*num_of_keys)
        self.Prime = prime
        self.maxInsertionTries = 10
        self.CuckooTables = [HashTable(a, b, self.NumOfSlots, self.Prime) for i in range(0, 2)]
        self.CuckooTables.append(LinkedList()) # Stash
        self.stash = 2

    def Insert(self, key):
        num_tries = 0
        whichTable = 0

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
                whichTable = (whichTable + 1) % 2

                hash_key = self.CuckooTables[whichTable].Hash(currentKey)
                num_tries += 1

            if num_tries > self.maxInsertionTries:
                whichTable = self.stash
                LinkedList.Insert(self.CuckooTables[whichTable], currentKey)
                break

    def Search(self, key):
        whichTable = 0
        hash_key = self.CuckooTables[whichTable].Hash(key)

        if self.CuckooTables[whichTable].Slot[hash_key].head.key == key:
            return whichTable, self.CuckooTables[whichTable].Slot[hash_key].head
        else:
            whichTable = 1
            hash_key = self.CuckooTables[whichTable].Hash(key)

            if self.CuckooTables[whichTable].Slot[hash_key].head.key == key:
                return whichTable, self.CuckooTables[whichTable].Slot[hash_key].head
            else:
                whichTable = self.stash
                return whichTable, self.CuckooTables[whichTable].Search(key)

    def Delete(self, element):
        whichTable, searchedElement = self.Search(element.key)
        if whichTable != self.stash:
            HashTable.Delete(self.CuckooTables[whichTable], searchedElement)
        else:
            LinkedList.Delete(self.CuckooTables[whichTable], searchedElement)

    def getSize(self):
        CuckooTableSize = [0, 0, 0]
        for i in range(0, 2):
            for j in range(0, self.NumOfSlots):
                CuckooTableSize[i] += self.CuckooTables[i].Slot[j].getSize()

        CuckooTableSize[self.stash] = self.CuckooTables[self.stash].getSize()
        return CuckooTableSize

if __name__ == "__main__":
    L = 10
    m = 40
    p = 8893
    A = [random.randint(1, 4081) for i in range(0, 2*m)]
    B = random.sample(A, m)

    a = random.randint(1, p-1)
    b = random.randint(0, p-1)

    C = Cuckoo(a, b, m, p)

    for i in range(0, m):
        C.Insert(B[i])

    print(C.getSize())

    for i in range(0, C.NumOfSlots):
        if C.CuckooTables[0].Slot[i].head != None and C.CuckooTables[0].Slot[i].head.key == B[13]:
            print(0, i, C.CuckooTables[0].Slot[i].head.key)

        if C.CuckooTables[1].Slot[i].head != None and C.CuckooTables[1].Slot[i].head.key == B[13]:
            print(1, i, C.CuckooTables[1].Slot[i].head.key)

    w, y = C.Search(B[13])
    C.Delete(y)
    print(C.getSize())
