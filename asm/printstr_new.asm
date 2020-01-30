; Prints Hello, world!
;
; Declares a subroutine that prints a string at a given address
;
; Expected output: Hello, world!

	LDI R0,Hello         ; address of "Hello, world!" bytes
	LDI R1,0             ; end string marker
	LDI R2,PrintStr      ; address of PrintStr
    LDI R3,PrintStrEnd   ; address of PrintStr
	CALL R2              ; call PrintStr
	HLT                  ; halt

; Subroutine: PrintStr
; R0 the address of the string

PrintStr:

	NOP

PrintStrLoop:     

	LD R4,R0            ; Load R3 from address in R0
    CMP R1,R4           ; Compare byte in R3 to 0
    JEQ R3              ; If 0, done printing, jump to end
	PRA R4              ; Print character

	INC R0              ; Increment pointer to next character

	LDI R4,PrintStrLoop ; Keep processing
	JMP R4

PrintStrEnd:
    LDI R0,Hello        ; Reset string pointer to beginning
	RET                 ; Return to caller

; Start of printable data

Hello:

	ds Hello, world!
	db 0x0a             ; newline
    db 0x00             ; end of string marker

