; Prints Hello, world! in a sine wave pattern
;
; Declares a subroutine that prints a string at a given address
;
; Expected output: Hello, world! repeatedly in an oscillating wave pattern

Start:
    LDI R0,SineTable     ; address of SineTable, also reused for address of Hello, world!
	LDI R1,0             ; end of loop / end of string marker
    LDI R2,32            ; ASCII value of space character
    LDI R3,Start         ; address of program start


; Subroutine: PrintStr
; R0 the address of the string
; R4 the address of the sine table for space offsets
; Print space characters to offset the string according to a sine pattern
; Then print the string
; Loop endlessly

Print:
	LD R5,R0            ; Load R5 from SineTable in R0
    CMP R5,R1           ; If at the end of SineTable
    JEQ R4              ; then start over

    LDI R3,PrintSpcLoop ; address of PrintSpcLoop
    LDI R4,PrintSpcEnd  ; address of PrintSpcEnd

PrintSpcLoop:
    DEC R5              ; Decrement spaces counter
    CMP R5,R1           ; Compare byte in R5 to 0 in R1
    JEQ R4              ; If 0, done printing spaces, jump to PrintSpcEnd
    
    PRA R2              ; Print spaces
    PRA R2
    PRA R2

    JMP R3              ; Loop back to PrintSpcLoop

PrintSpcEnd:
    INC R0              ; Increment pointer to next entry in SineTable
    PUSH R0             ; And push it to the stack for later retrieval
    LDI R0,Hello        ; Address of Hello, world!
    LDI R3,PrintStrLoop ; address of PrintStrLoop
    LDI R4,PrintStrEnd  ; address of PrintStrEnd

PrintStrLoop:
	LD R5,R0            ; Load R5 from address of Hello in R0
    CMP R5,R1           ; Compare byte in R5 to 0 in R1
    JEQ R4              ; If 0, done printing, jump to end

	PRA R5              ; Print character
	INC R0              ; Increment pointer to next character

	JMP R3              ; Keep processing string

PrintStrEnd:
    POP R0              ; Pop address of next SineTable entry into R0
    LDI R3,Print        ; Address of Print
    LDI R4,Start        ; Address of Start
	JMP R3              ; Loop back to Print

; SineTable is a lookup table containing the
; number of space characters to offset Hello, world!
; in order to create a sine wave pattern.
; 0x00 signifies end

SineTable:
    db 0x01
    db 0x01
    db 0x02
    db 0x03 
    db 0x04
    db 0x06
    db 0x08
    db 0x0a
    db 0x0b
    db 0x0c
    db 0x0e
    db 0x10
    db 0x12
    db 0x13
    db 0x14
    db 0x14
    db 0x14
    db 0x14
    db 0x13
    db 0x12
    db 0x10
    db 0x0e
    db 0x0c
    db 0x0b
    db 0x0a
    db 0x08
    db 0x06
    db 0x04
    db 0x03
    db 0x02
    db 0x01
    db 0x01
    db 0x00

; Start of printable data

SpcCharacter:
    db 0x09

Hello:
	ds Hello, world!
	db 0x0a             ; newline
    db 0x00             ; end of string marker
