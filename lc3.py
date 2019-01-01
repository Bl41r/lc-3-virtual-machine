"""LC-3 Virtual Machine.

A Python implementation of an LC-3 virtual machine, following along with the
tutorial (written in C) at https://justinmeiners.github.io/lc3-vm/index.html
"""

import sys
import array
from cpu import Lc3Cpu, ExecutionHalted


LOG_DUMP = []       # append debug messages here


def main(filename):
    """Main."""
    memory = load_rom_image(filename)
    cpu = Lc3Cpu(memory)

    try:
        while True:
            cpu.execute_next_instruction()

    except ExecutionHalted:     # raised by trap_halt
        print("\nShutting down LC-3 VM...")
        sys.exit(0)

    except (Exception, KeyboardInterrupt) as e:
        dump_logs(memory, cpu)
        raise e


def load_rom_image(filename):
    """Return a memory array with a ROM image loaded."""
    rom_array = array.array('H', range(0))
    with open(filename, 'rb') as f:
        rom_array.frombytes(f.read())

    if sys.byteorder == 'little':
        rom_array.byteswap()

    origin = rom_array[0]
    memory = array.array('H', range(0))
    for i in range(origin):     # fill with 0's up to origin address
        memory.append(0)
    for i in range(1, len(rom_array)):  # skips appending origin address (@i=0)
        memory.append(rom_array[i])
    for i in range((2**16) - len(memory)):  # fill remaining space with 0's
        memory.append(0)

    return memory


# Debugging

def dump_logs(memory, cpu):
    """Print all messages in LOG_DUMP."""
    print("\n\nLOG DUMP:")
    for item in LOG_DUMP:
        print(item)
    print()
    # print_mem_map(memory)   # print all non-zero values in memory
    print("Registers:", cpu.registers)


def print_mem_map(memory):
    """Print the memory map."""
    for i in range(2**16):
        if memory[i] != 0:
            print("val: {}  index: {}".format(memory[i], i))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: python3 lc3.py <rom_filename>")
        sys.exit(1)
    main(sys.argv[1])
