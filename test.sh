#!/bin/sh
SPACES=" . . . . . . . . . . . . . . . . . . . . . . . . "
for t in test_*.py; do
    echo -n "$t "
    python "$t" &> /dev/null
    echo -n "${SPACES:${#t}}"
    if [ $? == 0 ]; then
	echo -e "PASS"
    else
	echo -e "FAIL"
    fi
done
