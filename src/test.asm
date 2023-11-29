.data
    temp: .byte 1
    temp2: .byte 1

.text
    main:
        la		$t1, temp		# 
        la		$t2, temp2		# 
        add		$a0, $t1, $t2		# $t0 = $t1 + $t2
        li		$v0, 1		# $v0 = 4
        syscall

        li		$v0, 10		# $v0 = 10 
        syscall