# Element class containing the key, and pointers to prev, next Element
class Element:
	def __init__(self, key, prev=None, next = None):
		self.key = key
		if prev != None:
			self.prev = prev
		if next != None:
			self.next = next

class LinkedList:
	def __init__(self, element=None):
		self.head = None
		if element != None:
			Insert(self, element)

	def Insert(self, key):
		element = Element(key)
		element.next = self.head
		if self.head != None:
			self.head.prev = element

		self.head = element
		element.prev = None

	def Search(self, key):
		currentElement = self.head
		if currentElement != None:
			while currentElement.next != None and currentElement.key != key:
				currentElement = currentElement.next

			if currentElement.next == None and currentElement.key != key:
				return None
			else:
				return currentElement
		else:
			return None

	def Delete(self, element):
		if element != None:
			if element.prev != None:
				element.prev.next = element.next
			else:
				self.head = element.next

			if element.next != None:
				element.next.prev = element.prev

	def getSize(self):
		LinkedListSize = 0
		currentElement = self.head
		while currentElement != None:
			LinkedListSize += 1
			currentElement = currentElement.next
		return LinkedListSize
