#! -*- encoding:utf-8 -*-
class Hash(object):
	def __init__(self):
		self.Uid = None
	def rshift(self,val, n): 
		return (val % 0x100000000) >> n
	def hashCode(self,s):
		h = 0
		for c in s:
			h = (31 * h + ord(c)) & 0xFFFFFFFF
		return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000

	def toHexString(self,tag):
		HEX_DIGITS = [
			'0', '1', '2', '3', '4', '5', '6', '7',
			'8', '9', 'A', 'B', 'C', 'D', 'E', 'F'
		]

		ret = [
			HEX_DIGITS[(tag >> 28)],
			HEX_DIGITS[(tag >> 24) & 0xF],
			HEX_DIGITS[(tag >> 20) & 0xF],
			HEX_DIGITS[(tag >> 16) & 0xF],
			HEX_DIGITS[(tag >> 12) & 0xF],
			HEX_DIGITS[(tag >> 8) & 0xF],
			HEX_DIGITS[(tag >> 4) & 0xF],
			HEX_DIGITS[(tag >> 0) & 0xF]
		]

		return ''.join(ret)

	def getHash(self):
		str = self.Uid
		h = self.hashCode(str)
		print('HASH: ', h)

		shift = (h >> 28)
		#print('SHIFT: ', shift)
		shift = (h >> 24) & 0xF
		#print('SHIFT: ', shift)
		shift = (h >> 20) & 0xF
		#print('SHIFT: ', shift)
		shift = (h >> 16) & 0xF
		#print('SHIFT: ', shift)
		shift = (h >> 12) & 0xF
		#print('SHIFT: ', shift)
		shift = (h >> 8) & 0xF
		#print('SHIFT: ', shift)
		shift = (h >> 4) & 0xF
		#print('SHIFT: ', shift)
		shift = (h >> 0) & 0xF
		#print('SHIFT: ', shift)

		h = self.toHexString(h)
		#print('HEX: ', h)
		return h
#hash = Hash()
#hash.Uid = '1.2.276.0.20.1.2.4.185572756543.7644.1505846912.306274'
#hash.getHash()