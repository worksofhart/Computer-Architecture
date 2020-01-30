; Prints Hello, world! in a sine wave pattern
;
; Declares a subroutine that prints a string at a given address
;
; Expected output: Hello, world! repeatedly in an oscillating wave pattern

Start:
    LDI R0,SineTable     ; address of SineTable, also reused for address of Hello, world!
	LDI R1,255           ; end of loop / end of string marker
    LDI R2,32            ; ASCII value of space character
    LD R3,R0             ; Load R3 from SineTable in R0
    PUSH R3              ; Push onto stack because R3 also gets reused
    LDI R4,PrintSpcEnd   ; address of PrintSpcEnd

; Subroutine: PrintSpcLoop
; R0 the address of the SineTable
; R1 value of 255 used to mark end of SineTable
; R2 ASCII value of a space character
; R3 the value at the address in R0
;    reused for address of PrintSpcLoop to loop back to until done
; R4 address of PrintSpcEnd to jump to when done printing spaces
;
; Print R3 number of space characters from R2
; to offset the string according to a sine pattern.

PrintSpcLoop:
    POP R3
    DEC R3               ; Decrement spaces counter
    CMP R3,R1            ; Compare byte in R3 to 255 in R1
    JEQ R4               ; If 255, done printing spaces, jump to PrintSpcEnd
    
    PRA R2               ; Print spaces
    PRA R2
    PRA R2

    PUSH R3
    LDI R3,PrintSpcLoop  ; address of PrintSpcLoop
    JMP R3               ; Loop back to PrintSpcLoop

PrintSpcEnd:
    INC R0               ; Increment pointer to next entry in SineTable
    PUSH R0              ; And push it to the stack for later retrieval
    LDI R0,Hello         ; Address of Hello, world!
    LDI R3,PrintStrLoop  ; address of PrintStrLoop
    LDI R4,PrintStrEnd   ; address of PrintStrEnd

; Subroutine: PrintStrLoop
; R0 the address of the string Hello, world!
; R1 value of 255 used to mark end of string
; R3 the value at the address in R0
;    reused for address of PrintStrLoop to loop back to until done
; R4 address of PrintStrEnd to jump to when done printing spaces
;
; Print characters one at a time from R3 until end of string.

PrintStrLoop:
	LD R3,R0             ; Load R3 from address of Hello in R0
    CMP R3,R1            ; Compare byte in R3 to 255 in R1
    JEQ R4               ; If 255, done printing, jump to end

	PRA R3               ; Print character
	INC R0               ; Increment pointer to next character

    LDI R3,PrintStrLoop  ; address of PrintStrLoop
	JMP R3               ; Keep processing string

PrintStrEnd:
    LDI R4,Start         ; Address of Start

    POP R0               ; Pop address of next SineTable entry into R0
    LD R3,R0             ; Load R3 from SineTable in R0
    CMP R3,R1            ; Compare byte in R3 to 255 in R1
    JEQ R4               ; Start over

    PUSH R3
    LDI R3,PrintSpcLoop  ; address of PrintSpcLoop
    LDI R4,PrintSpcEnd   ; address of PrintSpcEnd
	JMP R3               ; Loop back to PrintSpcLoop

; SineTable is a lookup table containing the
; number of space characters to offset Hello, world!
; in order to create a sine wave pattern.
; 0xff signifies end

SineTable:
    db 0x00
    db 0x00
    db 0x01
    db 0x02 
    db 0x03
    db 0x05
    db 0x07
    db 0x09
    db 0x0a
    db 0x0b
    db 0x0d
    db 0x0f
    db 0x11
    db 0x12
    db 0x13
    db 0x13
    db 0x13
    db 0x13
    db 0x12
    db 0x11
    db 0x0f
    db 0x0d
    db 0x0b
    db 0x0a
    db 0x09
    db 0x07
    db 0x05
    db 0x03
    db 0x02
    db 0x01
    db 0x00
    db 0x00
    db 0xff

; Start of printable data

Hello:
	ds Hello, world!
	db 0x0a              ; newline
    db 0xff              ; end of string marker
