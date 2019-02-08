from linked_list import LinkedList
import random

# Hash class: simple hash function
# Should use higher quality k-universal hash functions but this seems to do the trick
class HashFunctionClass:
	def __init__(self, a, b, num_of_slots, prime):
		self.a = a
		self.b = b
		self.NumOfSlots = num_of_slots
		self.Prime = prime

	def Hash(self, key):
		return ((self.a*key + self.b) % self.Prime ) % self.NumOfSlots

# Implementation of a chained hash table
class HashTable(HashFunctionClass):
	def __init__(self, a, b, num_of_slots, prime):
		self.Slot = []
		HashFunctionClass.__init__(self, a, b, num_of_slots, prime)
		for i in range(0, self.NumOfSlots):
			self.Slot.append(LinkedList())

	def Insert(self, key):
		self.Slot[self.Hash(key)].Insert(key)

	def Search(self, key):
		element = self.Slot[self.Hash(key)].Search(key)
		return element

	def Delete(self, element):
		if element != None:
			self.Slot[self.Hash(element.key)].Delete(element)

	def getSize(self):
		HashTableSize = 0
		for i in range(0, len(self.Slot)):
			HashTablesize += self.Slot.getSize()
		return HashTableSize
