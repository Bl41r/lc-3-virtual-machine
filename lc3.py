"""LC-3 Virtual Machine.

A Python implementation of an LC-3 virtual machine, based on the
tutorial (written in C) at https://justinmeiners.github.io/lc3-vm/index.html
"""

import sys
from memory import Lc3Memory
from cpu import Lc3Cpu, ExecutionHalted


LOG_DUMP = []   # append debug messages here


def main(filename):
    """Main."""
    lc3_memory = Lc3Memory()
    lc3_memory.load_rom_image(filename)
    cpu = Lc3Cpu(lc3_memory.memory)

    try:
        while True:
            cpu.execute_next_instruction()

    except ExecutionHalted:     # raised by trap_halt (expected exit)
        print("\nShutting down LC-3 VM...")
        sys.exit(0)

    except (Exception, KeyboardInterrupt) as e:
        dump_logs(lc3_memory.memory, cpu)
        raise e


# Debugging

def dump_logs(memory, cpu):
    """Print all messages in LOG_DUMP."""
    print("\n\nLOG DUMP:")
    for item in LOG_DUMP:
        print(item)
    print()
    # print_mem_map(memory)
    print("Registers:", cpu.registers)


def print_mem_map(memory):
    """Print all non-zero values in memory."""
    for i in range(2**16):
        if memory[i] != 0:
            print("val: {}  index: {}".format(memory[i], i))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: python3 lc3.py <rom_filename>")
        sys.exit(1)
    main(sys.argv[1])
