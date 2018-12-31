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
        execute_one_cycle()


def execute_one_cycle():
    """Execute one operation cycle."""
    rpc = CPU.registers[RPC_REGISTER_INDEX]     # get current rpc
    CPU.increment_rpc()                     # increment rpc
    CPU.execute_instruction(CPU.mem_read(rpc))  # execute instruction @ rpc


def load_rom_image(filename):
    """Load a ROM image into MEMORY."""
    print("Loading " + filename)

    # find the origin (where in memory array to start loading the rom)
    # the origin is the first 16-bit word in the image
    origin_array = array.array('H', range(1))
    with open(filename, 'rb') as f:
        origin_array.fromfile(f, 1)
        if sys.byteorder == "little":
            origin_array.byteswap()
    origin = origin_array[1]

    # initialize memory array of zeros up to origin-1
    for i in range(origin - 1):
        MEMORY.append(0)

    # append unsigned shorts in image to memory array
    with open(filename, 'rb') as f:
        MEMORY.frombytes(f.read())
        MEMORY[origin - 1] = 0      # overwrite this back to 0
        if sys.byteorder == "little":
            MEMORY.byteswap()

    # append zeros to rest of available memory
    if len(MEMORY) < 2**16:
        for i in range(2**16 - len(MEMORY)):
            MEMORY.append(0)


def dump_logs():
    """Print all messages in LOG_DUMP."""
    print("\n\nLOG DUMP:")
    for item in LOG_DUMP:
        print(item)
    print()
    # print_mem_map()
    print("Registers:", CPU.registers)


def print_mem_map():
    """Print the memory map."""
    for i in range(2**16):
        if MEMORY[i] != 0:
            print("val: {}  index: {}".format(MEMORY[i], i))


if __name__ == '__main__':
    main(sys.argv[1])
