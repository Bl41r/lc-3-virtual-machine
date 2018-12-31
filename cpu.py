"""LC-3 self."""

import ctypes
import getch
import sys

FLAGS = {
    'FL_POS': 1 << 0,
    'FL_ZRO': 1 << 1,
    'FL_NEG': 1 << 2
}

PC_START = 0x3000
RPC_REG_INDEX = 8
RCOND_REG_INDEX = 9

MEM_REGISTERS = {
    'MR_KBSR': 0xFE00,
    'MR_KBDR': 0xFE02
}


def ushort(val):
    """Return unsigned short value."""
    return ctypes.c_ushort(val).value


def sign_extend(x, bit_count):
    """Extend number of bits for positive or negative x."""
    tmp = x >> (bit_count - 1) & 1
    if (tmp):
        x = ushort(x | (0xFFFF << bit_count))
    return x


class ExecutionHalted(Exception):
    """Raised when halt trap is issued."""

    pass


class Lc3Cpu(object):
    """LC-3 CPU."""

    def __init__(self, memory):
        """Initialize cpu with a pointer to system memory."""
        self.memory = memory

        # registers: r0 - r7, r_pc, r_cond
        self.registers = [0, 0, 0, 0, 0, 0, 0, 0, PC_START, 0]
        self.getch = getch._Getch()
        self._opcodes = {
            0: ('OP_BR', self._op_br),     # branch
            1: ('OP_ADD', self._op_add),    # add
            2: ('OP_LD', self._op_ld),     # load
            3: ('OP_ST', self._op_st),     # store
            4: ('OP_JSR', self._op_jsr),    # jump register
            5: ('OP_AND', self._op_and),    # and
            6: ('OP_LDR', self._op_ldr),    # load register
            7: ('OP_STR', self._op_str),    # store register
            8: ('OP_RTI', self._op_rti),    # unused
            9: ('OP_NOT', self._op_not),    # not
            10: ('OP_LDI', self._op_ldi),   # load indirect
            11: ('OP_STI', self._op_sti),   # store indirect
            12: ('OP_JMP', self._op_jmp),   # jump
            13: ('OP_RES', self._op_res),   # reserved (unused)
            14: ('OP_LEA', self._op_lea),   # load effective address
            15: ('OP_TRAP', self._op_trap)   # execute trap
        }
        self._traps = {
            0x20: self._trap_getc,
            0x21: self._trap_out,
            0x22: self._trap_puts,
            0x23: self._trap_in,
            0x24: self._trap_putsp,
            0x25: self._trap_halt
        }

    def execute_instruction(self, instruction):
        """Execute an instruction."""
        self._opcodes[instruction >> 12][1](instruction)

    def increment_rpc(self):
        """Increment rpc."""
        self.registers[RPC_REG_INDEX] = ushort(
            self.registers[RPC_REG_INDEX] + 1)

    def mem_read(self, address):
        """Read address in MEMORY."""
        if (address == ushort(MEM_REGISTERS['MR_KBSR'])):
            key = self._check_key()
            if (key):
                self.memory[MEM_REGISTERS['MR_KBSR']] = (1 << 15)
                self.memory[MEM_REGISTERS['MR_KBDR']] = key
            else:
                self.memory['MR_KBSR'] = 0
        return self.memory[address]

    def mem_write(self, address, val):
        """Write val to address in MEMORY."""
        self.memory[address] = val

    def _get_char(self):
        """Get one char."""
        return ushort(ord(self.getch()))

    def _check_key():
        """Check if a key is being pressed I think..."""
        key = ""
        raise Exception("called check key, not implemented")
        # for i in range(1000):
        #     try:
        #         key = see_if_a_key_is_pressed_down
        #         if key != '':
        #             return key
        #     except Exception as e:
        #         pass
        return None

    def _update_flags(self, register_index):
        """Update rcond register."""
        value = self.registers[register_index]
        if value == 0:
            self.registers[RCOND_REG_INDEX] = FLAGS['FL_ZRO']
        elif value >> 15:
            self.registers[RCOND_REG_INDEX] = FLAGS['FL_NEG']
        else:
            self.registers[RCOND_REG_INDEX] = FLAGS['FL_POS']

    # Opcodes
    def _op_add(self, instruction):
        """ADD opcode."""
        r0 = (instruction >> 9) & 0x7
        r1 = (instruction >> 6) & 0x7
        imm_flag = (instruction >> 5) & 0x1

        if (imm_flag):
            imm5 = sign_extend(instruction & 0x1F, 5)
            self.registers[r0] = ushort(self.registers[r1] + imm5)
        else:
            r2 = instruction & 0x7
            self.registers[r0] = ushort(
                self.registers[r1] + self.registers[r2]
            )
        self._update_flags(r0)

    def _op_br(self, instruction):
        """BRANCH opcode."""
        pc_offset = sign_extend((instruction) & 0x1ff, 9)
        cond_flag = (instruction >> 9) & 0x7
        if cond_flag & self.registers[RCOND_REG_INDEX]:
            self.registers[RPC_REG_INDEX] = ushort(
                self.registers[RPC_REG_INDEX] + pc_offset
            )

    def _op_ld(self, instruction):
        """LOAD opcode."""
        r0 = (instruction >> 9) & 0x7
        pc_offset = sign_extend(instruction & 0x1ff, 9)
        reg_with_offset = ushort(self.registers[RPC_REG_INDEX] + pc_offset)
        self.registers[r0] = self.mem_read(reg_with_offset)
        self._update_flags(r0)

    def _op_st(self, instruction):
        """STORE opcode."""
        r0 = (instruction >> 9) & 0x7
        pc_offset = sign_extend(instruction & 0x1ff, 9)
        address = ushort(self.registers[RPC_REG_INDEX] + pc_offset)
        self.mem_write(address, self.registers[r0])

    def _op_jsr(self, instruction):
        """JUMP REGISTER opcode."""
        r1 = (instruction >> 6) & 0x7
        long_pc_offset = sign_extend(instruction & 0x7ff, 11)
        self.registers[7] = self.registers[RPC_REG_INDEX]

        long_flag = (instruction >> 11) & 1
        if long_flag:
            self.registers[RPC_REG_INDEX] = ushort(
                self.registers[RPC_REG_INDEX] + long_pc_offset)
        else:
            self.registers[RPC_REG_INDEX] = self.registers[r1]

    def _op_and(self, instruction):
        """AND opcode."""
        r0 = (instruction >> 9) & 0x7
        r1 = (instruction >> 6) & 0x7
        imm_flag = (instruction >> 5) & 0x1
        if imm_flag:
            imm5 = sign_extend(instruction & 0x1F, 5)
            self.registers[r0] = ushort(self.registers[r1] & imm5)
        else:
            r2 = instruction & 0x7
            self.registers[r0] = ushort(
                self.registers[r1] & self.registers[r2]
            )
        self._update_flags(r0)

    def _op_ldr(self, instruction):
        """LOAD register."""
        r0 = (instruction >> 9) & 0x7
        r1 = (instruction >> 6) & 0x7
        offset = sign_extend(instruction & 0x3F, 6)
        self.registers[r0] = self.mem_read(
            ushort(self.registers[r1] + offset)
        )
        self._update_flags(r0)

    def _op_str(self, instruction):
        """STORE REGISTER opcode."""
        r0 = (instruction >> 9) & 0x7
        r1 = (instruction >> 6) & 0x7
        offset = sign_extend(instruction & 0x3F, 6)
        reg_with_offset = ushort(self.registers[r1] + offset)
        self.mem_write(reg_with_offset, self.registers[r0])

    def _op_rti(self, instruction):
        """An unused opcode."""
        raise Exception("opcode not implemented!")

    def _op_not(self, instruction):
        """NOT opcode."""
        r0 = (instruction >> 9) & 0x7
        r1 = (instruction >> 6) & 0x7
        self.registers[r0] = ~self.registers[r1]
        self._update_flags(r0)

    def _op_ldi(self, instruction):
        """LOAD INDIRECT."""
        r0 = (instruction >> 9) & 0x07
        pc_offset = sign_extend(instruction & 0x1ff, 9)
        self.registers[r0] = self.mem_read(
            self.mem_read(ushort(
                self.registers[RPC_REG_INDEX] + pc_offset)
            )
        )
        self._update_flags(r0)

    def _op_sti(self, instruction):
        """STORE INDIRECT opcode."""
        raise Exception("opcode not implemented!")

    def _op_jmp(self, instruction):
        """JUMP opcode."""
        r1 = (instruction >> 6) & 0x7
        self.registers[RPC_REG_INDEX] = self.registers[r1]

    def _op_res(vinstruction):
        """Reserved opcode."""
        raise Exception("opcode not implemented!")

    def _op_lea(self, instruction):
        """LOAD EFFECTIVE ADDRESS opcode."""
        r0 = (instruction >> 9) & 0x7
        pc_offset = sign_extend(instruction & 0x1ff, 9)

        self.registers[r0] = ushort(
            self.registers[RPC_REG_INDEX] + pc_offset)

        self._update_flags(r0)

    # Traps
    def _op_trap(self, instruction):
        """TRAP opcode."""
        trap_code = instruction & 0xFF
        self._traps[trap_code]()

    def _trap_getc(self):
        """Read a single char."""
        self.registers[0] = self._get_char()

    def _trap_out(self):
        """Put char out."""
        char_code = self.registers[0]
        print(chr(char_code), end='', flush=True)

    def _trap_puts(self):
        """Write to stdout."""
        current_location = self.registers[0]
        while self.memory[current_location]:
            char_code = self.memory[current_location]
            print(chr(char_code), end='')
            current_location = ushort(current_location + 1)
        sys.stdout.flush()

    def _trap_in(self):
        """Enter char."""
        raise Exception("Trap not implemented yet!")

    def _trap_putsp(self):
        """Put multiple chars to stdout."""
        raise Exception("Trap not implemented yet!")

    def _trap_halt(self):
        """Put HALT."""
        print("HALT")
        sys.stdout.flush()
        raise ExecutionHalted
