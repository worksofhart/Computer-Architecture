"""CPU functionality."""

import sys
from interrupts import Interrupts


# Register name constants
IM = 5  # Interrupt Mask, reg R5
IS = 6  # Interrupt Status, reg R6
SP = 7  # Stack Pointer, reg R7

# Instruction lookup
ADD = 0b10100000
AND = 0b10101000
CALL = 0b01010000
CMP = 0b10100111
DEC = 0b01100110
DIV = 0b10100011
HLT = 0b00000001  # HLT
INC = 0b01100101
INT = 0b01010010
IRET = 0b00010011
JEQ = 0b01010101
JGE = 0b01011010
JGT = 0b01010111
JLE = 0b01011001
JLT = 0b01011000
JMP = 0b01010100
JNE = 0b01010110
LD = 0b10000011
LDI = 0b10000010  # LDI register immediate
MOD = 0b10100100
MUL = 0b10100010
NOP = 0b00000000
NOT = 0b01101001
OR = 0b10101010
POP = 0b01000110
PRA = 0b01001000
PRN = 0b01000111
PUSH = 0b01000101
RET = 0b00010001
SHL = 0b10101100
SHR = 0b10101101
ST = 0b10000100
SUB = 0b10100001
XOR = 0b10101011

# Register mask
# Isolate register number in instructions which operate on registers
REG_MASK = 0b00000111

# Byte mask
# Used to limit results to 8 bits
BYTE_MASK = 0b11111111


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        # 256 bytes of RAM
        self.ram = [0] * 256
        # Registers R0 - R7
        self.reg = [0] * 8
        # Start of stack
        self.reg[SP] = 0xF3

        # Internal registers
        # Program Counter, address of the currently executing instruction
        self.PC = 0x00
        # Instruction Register, contains a copy of the currently executing instruction
        self.IR = 0x00
        # Flags, 0b00000LGE (less-than, greater-than, equal)
        self.FL = 0b00000000
        # Whether halted or not
        self.halted = False
        # Whether interrupts are currently disabled
        self.interrupts_disabled = False

        # Instruction jump table
        self.jumptable = {
            ADD: self.handle_ADD,
            AND: self.handle_AND,
            CALL: self.handle_CALL,
            CMP: self.handle_CMP,
            DEC: self.handle_DEC,
            DIV: self.handle_DIV,
            HLT: self.handle_HLT,
            INC: self.handle_INC,
            INT: self.handle_INT,
            IRET: self.handle_IRET,
            JEQ: self.handle_JEQ,
            JGE: self.handle_JGE,
            JGT: self.handle_JGT,
            JLE: self.handle_JLE,
            JLT: self.handle_JLT,
            JMP: self.handle_JMP,
            JNE: self.handle_JNE,
            LD: self.handle_LD,
            LDI: self.handle_LDI,
            MUL: self.handle_MUL,
            NOP: self.handle_NOP,
            NOT: self.handle_NOT,
            OR: self.handle_OR,
            POP: self.handle_POP,
            PRA: self.handle_PRA,
            PRN: self.handle_PRN,
            PUSH: self.handle_PUSH,
            RET: self.handle_RET,
            SHL: self.handle_SHL,
            SHR: self.handle_SHR,
            ST: self.handle_ST,
            SUB: self.handle_SUB,
            XOR: self.handle_XOR
        }

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self, program):
        """Load a program into memory."""

        address = 0

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b=0):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            if self.reg[reg_b] != 0:
                self.reg[reg_a] //= self.reg[reg_b]
            else:
                self.halted = True
                raise Exception("Division by zero error")
        elif op == "MOD":
            if self.reg[reg_b] != 0:
                self.reg[reg_a] %= self.reg[reg_b]
            else:
                self.halted = True
                raise Exception("Division by zero error")
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == "SHL":
            self.reg[reg_a] <<= self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] >>= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL = 0b100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL = 0b010
        else:
            self.halted = True
            raise Exception("Unsupported ALU operation")

        self.reg[reg_a] &= BYTE_MASK

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            # self.fl,
            # self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print(" | %02X |" % self.reg[SP], end="")
        for i in range(230, 243):
            print(" %02X" % self.ram[i], end='')

        print(" | ", end='')
        for i in range(243, 256):
            print(" %02X" % self.ram[i], end='')

        print()

    # Execute the currently loaded program
    def run(self):
        """Run the CPU."""

        with Interrupts(regs=self.reg) as interrupts:
            self.interrupts = interrupts

            # Execute instructions until a HLT instruction or invalid state reached
            while not self.halted:
                # Store most recently pressed key in 0xF4
                self.ram_write(0xF4, interrupts.keypressed)
                # input()

                # INTERRUPT SERVICING - select only watched-for interrupts by masking
                masked_interrupts = self.reg[IS] & self.reg[IM]

                # If watched-for interrupts exist, have been triggered, and are currently enabled
                if masked_interrupts and interrupts.ENABLED:
                    # Loop through bits of masked interrupts from low to high
                    i = 0
                    while i <= 7 and interrupts.ENABLED:
                        bit_mask = 1 << i
                        # If selected bit is set, prepare to service interrupt
                        if masked_interrupts & bit_mask:
                            # Turn off interrupts
                            interrupts.ENABLED = False
                            # Clear selected Interrupt Status Bit
                            self.reg[IS] ^= bit_mask
                            # Push PC, FL, and R0 - R6 to stack
                            self.handle_PUSH(self.PC)
                            self.handle_PUSH(self.FL)
                            for r in range(7):
                                self.handle_PUSH(self.reg[r])
                            # Put address from selected interrupt vector in PC
                            self.PC = self.ram_read(0xF8 + i)
                        i += 1

                # self.trace()
                # print()

                # Load the instruction register
                self.IR = self.ram_read(self.PC)

                # If a known instruction is found, execute it
                if self.IR in self.jumptable:
                    self.jumptable[self.IR]()

                    # If the instruction doesn't set PC directly, advance to next instruction
                    if not self.IR & 0b00010000:
                        self.PC += (self.IR >> 6) + 1

                else:
                    # Quit on unknown instruction
                    raise Exception(
                        f"Unimplemented instruction 0x{self.IR:02x} at 0x{self.PC:02x}")
                    self.halted = True

                # Kill switch from interrupt source, currently triggered by hitting ESC key
                if interrupts.DONE:
                    self.halted = True
            interrupts.stop()

    # Instructions
    def handle_ADD(self):
        """
        ADD registerA registerB
        Add the value in two registers and store the result in registerA.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2) & REG_MASK
        self.alu("ADD", operand_a, operand_b)

    def handle_AND(self):
        """
        AND registerA registerB
        Bitwise-AND the values in registerA and registerB, then store the result in registerA.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2) & REG_MASK
        self.ALU("AND", operand_a, operand_b)

    def handle_CALL(self):
        """
        CALL register
        Calls a subroutine at the address stored in the register.
        """
        # Address to return to
        operand_a = self.PC + 2
        # Address to jump to in specified register
        operand_b = self.reg[self.ram_read(self.PC + 1) & REG_MASK]

        self.handle_PUSH(operand_a)
        # Set PC to address in specified register
        self.PC = operand_b

    def handle_CMP(self):
        """
        CMP registerA registerB
        Compare the values in two registers and set flags accordingly.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2) & REG_MASK
        self.alu("CMP", operand_a, operand_b)

    def handle_DEC(self):
        """
        DEC register
        Decrement (subtract 1 from) the value in the given register.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        self.reg[operand_a] -= 1
        self.reg[operand_a] &= BYTE_MASK

    def handle_DIV(self):
        """
        SUB registerA registerB
        Divide the value in the first register by the value in the second, storing the result in registerA.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2) & REG_MASK
        self.alu("DIV", operand_a, operand_b)

    def handle_HLT(self):
        """
        HLT
        Halt the CPU.
        """
        self.halted = True

    def handle_INC(self):
        """
        INC register
        Increment (add 1 to) the value in the given register.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        self.reg[operand_a] += 1
        self.reg[operand_a] &= BYTE_MASK

    def handle_INT(self):
        """
        INT register
        Issue the interrupt number stored in the given register.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        self.reg[IS] |= 1 << operand_a

    def handle_IRET(self):
        """
        IRET
        Return from an interrupt handler.
        """
        for r in reversed(range(7)):
            self.reg[r] = self.handle_POP()
        self.FL = self.handle_POP()
        self.PC = self.handle_POP()
        self.interrupts.ENABLED = True

    def handle_JEQ(self):
        """
        JEQ register
        If equal flag is set (true), jump to the address stored in the given register.
        """
        if self.FL & 0b001:
            operand_a = self.ram_read(self.PC+1) & REG_MASK
            self.handle_JMP(self.reg[operand_a])
        else:
            self.PC += 2

    def handle_JGE(self):
        """
        JGE register
        If greater-than flag or equal flag is set (true), jump to the address stored in the given register.
        """
        if self.FL & 0b011:
            operand_a = self.ram_read(self.PC+1) & REG_MASK
            self.handle_JMP(self.reg[operand_a])
        else:
            self.PC += 2

    def handle_JGT(self):
        """
        JGT register
        If greater-than flag is set (true), jump to the address stored in the given register.
        """
        if self.FL & 0b010:
            operand_a = self.ram_read(self.PC+1) & REG_MASK
            self.handle_JMP(self.reg[operand_a])
        else:
            self.PC += 2

    def handle_JLE(self):
        """
        JLE register
        If less-than flag or equal flag is set (true), jump to the address stored in the given register.
        """
        if self.FL & 0b101:
            operand_a = self.ram_read(self.PC+1) & REG_MASK
            self.handle_JMP(self.reg[operand_a])
        else:
            self.PC += 2

    def handle_JLT(self):
        """
        JLT register
        If less-than flag is set (true), jump to the address stored in the given register.
        """
        if self.FL & 0b100:
            operand_a = self.ram_read(self.PC+1) & REG_MASK
            self.handle_JMP(self.reg[operand_a])
        else:
            self.PC += 2

    def handle_JMP(self, addr=None):
        """
        JMP register
        Jump to the address stored in the given register.
        """
        if addr is None:
            operand_a = self.ram_read(self.PC+1) & REG_MASK
        self.PC = self.reg[operand_a] if addr is None else addr

    def handle_JNE(self):
        """
        JNE register
        If E flag is clear (false, 0), jump to the address stored in the given register.
        """
        if not self.FL & 0b001:
            operand_a = self.ram_read(self.PC+1) & REG_MASK
            self.handle_JMP(self.reg[operand_a])
        else:
            self.PC += 2

    def handle_LD(self):
        """
        LD registerA registerB
        Loads registerA with the value at the memory address stored in registerB.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2) & REG_MASK
        self.reg[operand_a] = self.ram_read(self.reg[operand_b])

    def handle_LDI(self):
        """
        LDI register immediate
        Set the value of a register to an integer.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2)
        self.reg[operand_a] = operand_b

    def handle_MOD(self):
        """
        MOD registerA registerB
        Divide the value in the first register by the value in the second, storing the remainder of the result in registerA.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2) & REG_MASK
        self.alu("MOD", operand_a, operand_b)

    def handle_MUL(self):
        """
        MUL registerA registerB
        Multiply the values in two registers together and store the result in registerA.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2) & REG_MASK
        self.alu("MUL", operand_a, operand_b)

    def handle_NOP(self):
        """
        NOP
        No operation. Do nothing for this instruction.
        """
        pass

    def handle_NOT(self):
        """
        NOT register
        Perform a bitwise-NOT on the value in a register.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        self.alu("NOT", operand_a)

    def handle_OR(self):
        """
        OR registerA registerB
        Bitwise-OR the values in registerA and registerB, then store the result in registerA.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2) & REG_MASK
        self.ALU("OR", operand_a, operand_b)

    def handle_POP(self):
        """
        POP register
        Pop the value at the top of the stack into the given register.
        """

        operand_a = self.ram_read(self.PC+1) & REG_MASK
        popped = self.ram_read(self.reg[SP])
        self.reg[operand_a] = popped
        self.reg[SP] += 1
        self.reg[SP] &= BYTE_MASK
        return popped

    def handle_PRA(self):
        """
        PRA register pseudo-instruction
        Print alpha character value stored in the given register.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        print(chr(self.reg[operand_a]), end='', flush=True)

    def handle_PRN(self):
        """
        PRN register (pseudo-instruction)
        Print numeric value stored in the given register.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        print(self.reg[operand_a])

    def handle_PUSH(self, val=None):
        """
        PUSH register
        Push the value in the given register on the stack.
        If val given in function call, push val instead
        """
        if val is None:
            operand_a = self.ram_read(self.PC+1) & REG_MASK
        self.reg[SP] -= 1
        self.reg[SP] &= BYTE_MASK
        self.ram_write(self.reg[SP], self.reg[operand_a]
                       if val is None else val)

    def handle_RET(self):
        """
        RET
        Return from subroutine.
        """
        # Pop return address from stack and set PC
        self.PC = self.ram_read(self.reg[SP])
        # Increment Stack Pointer
        self.reg[SP] -= 1
        self.reg[SP] &= BYTE_MASK

    def handle_SHL(self):
        """
        SHL registerA registerB
        Shift the value in registerA left by the number of bits specified in registerB, filling the low bits with 0.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2) & REG_MASK
        self.ALU("AND", operand_a, operand_b)

    def handle_SHR(self):
        """
        SHR registerA registerB
        Shift the value in registerA right by the number of bits specified in registerB, filling the high bits with 0.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2) & REG_MASK
        self.ALU("AND", operand_a, operand_b)

    def handle_ST(self):
        """
        ST registerA registerB
        Store value in registerB in the address stored in registerA.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2) & REG_MASK
        self.ram_write(self.reg[operand_a], self.reg[operand_b])

    def handle_SUB(self):
        """
        SUB registerA registerB
        Subtract the value in the second register from the first, storing the result in registerA.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2) & REG_MASK
        self.alu("SUB", operand_a, operand_b)

    def handle_XOR(self):
        """
        XOR registerA registerB
        Bitwise-XOR the values in registerA and registerB, then store the result in registerA.
        """
        operand_a = self.ram_read(self.PC+1) & REG_MASK
        operand_b = self.ram_read(self.PC+2) & REG_MASK
        self.ALU("XOR", operand_a, operand_b)
