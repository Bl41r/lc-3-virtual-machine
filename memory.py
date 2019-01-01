"""Memory for the LC-3."""

import array
import sys


class Lc3Memory(object):
	"""Memory of the LC-3 VM."""

	def __init__(self):
		self.mem_size = 2**16
		self.memory = array.array('H', range(self.mem_size))
		
	def load_rom_image(self, filename):
	    """Return a memory array with a ROM image loaded."""
	    self._clear_memory()
	    rom_array = self._read_rom_file(filename)
	    origin = rom_array[0]

	    for i in range(1, len(rom_array)):  # skips appending origin address (@i=0)
	        self.memory[origin+i] = rom_array[i]

	def _read_rom_file(self, filename):
	    """Return an array containing ROM file."""
	    rom_array = array.array('H', range(0))
	    with open(filename, 'rb') as f:
	        rom_array.frombytes(f.read())

	    if sys.byteorder == 'little':
	        rom_array.byteswap()
	    
	    return rom_array

	def _clear_memory(self):
		"""Reset all memory slots to 0."""
		for i in range(self.mem_size):
			self.memory[i] = 0
