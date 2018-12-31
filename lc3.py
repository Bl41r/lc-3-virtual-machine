"""LC-3 Virtual Machine.

A Python implementation of an LC-3 virtual machine, following along with the
tutorial (written in C) at https://justinmeiners.github.io/lc3-vm/index.html
"""

import sys
import array
from cpu import Lc3Cpu, ExecutionHalted, RPC_REGISTER_INDEX


LOG_DUMP = []       # append debug messages here
MEMORY = array.array('H', range(0))     # populated when ROM loaded
CPU = Lc3Cpu(MEMORY)


def main(filename):
    """Main."""
    load_rom_image(filename)

    try:
        execute()

    except ExecutionHalted:     # raised by trap_halt
        print("\nShutting down...")
        sys.exit(0)

    except (Exception, KeyboardInterrupt) as e:
        dump_logs()
        raise e


def execute():
    """Execute the loaded program."""
    while True:
        curr_rpc = CPU.registers[RPC_REGISTER_INDEX]     # get current rpc
        CPU.increment_rpc()                             # increment rpc
        CPU.execute_instruction(CPU.mem_read(curr_rpc))  # execute instr @ rpc


def load_rom_image(filename):
    """Load a ROM image into MEMORY."""
    print("Loading rom: " + filename + "\n")
    rom_array = array.array('H', range(0))
    with open(filename, 'rb') as f:
        rom_array.frombytes(f.read())

    if sys.byteorder == 'little':
        rom_array.byteswap()

    origin = rom_array[0]
    for i in range(origin):
        MEMORY.append(0)

    for i in range(1, len(rom_array)):  # Don't need to append origin
        MEMORY.append(rom_array[i])

    for i in range((2**16) - len(MEMORY)):
        MEMORY.append(0)


# Debugging

def dump_logs():
    """Print all messages in LOG_DUMP."""
    print("\n\nLOG DUMP:")
    for item in LOG_DUMP:
        print(item)
    print()
    # print_mem_map()   # print all non-zero values in memory
    print("Registers:", CPU.registers)


def print_mem_map():
    """Print the memory map."""
    for i in range(2**16):
        if MEMORY[i] != 0:
            print("val: {}  index: {}".format(MEMORY[i], i))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: python3 lc3.py <rom_filename>")
        sys.exit(1)
    main(sys.argv[1])
