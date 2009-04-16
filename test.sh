#!/bin/sh
SPACES=" . . . . . . . . . . . . . . . . . . . . . . . . "
for t in test_*.py; do
    echo -n "$t "
    echo -n "${SPACES:${#t}}"
    python "$t" &> /dev/null
    if [ $? == 0 ]; then
	echo -e "PASS"
    else
	echo -e "FAIL"
    fi
done
