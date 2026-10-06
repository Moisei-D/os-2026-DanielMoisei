#!/bin/bash

# Run this file from the directory that contains access.log:
#   bash oneliners.sh

# Q1. How many requests failed?
grep -c FAIL access.log

# Q2. How many different pages were requested, and which?
cut -d' ' -f5 access.log | sort -u | awk 'BEGIN { print "Requested pages:" } { pages[NR]=$0 } END { for (i=1; i<=NR; i++) print pages[i]; print "Number of different pages: " NR }'

# Q3. How many requests did each page get?
cut -d' ' -f5 access.log | sort | uniq -c | sort -rn

# Q4. Which user or users have the most failed requests, and how many?
grep FAIL access.log | cut -d' ' -f3 | sort | uniq -c | sort -rn | awk 'NR == 1 { maximum=$1 } $1 == maximum'

# Q5. How many requests did user3 make, and how many of them failed?
printf 'user3 requests: '; grep -c ' user3 ' access.log; printf 'user3 failed requests: '; grep ' user3 ' access.log | grep -c FAIL

# Q6. Print the last 3 failed requests, showing only time and user.
grep FAIL access.log | tail -3 | cut -d' ' -f2-3

# Q7. Which login shells appear in /etc/passwd, and how many accounts use each?
cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn

# Q8. Why do the two counts differ by exactly one? Run both for comparison.
printf 'ls /etc count: '; ls /etc | wc -l; printf 'ls -l /etc count: '; ls -l /etc | wc -l

# Bonus. Lines where the minute ends in 0 and the request failed, followed by their count.
grep -E '10:[0-5]0 .* FAIL' access.log; printf 'Bonus count: '; grep -Ec '10:[0-5]0 .* FAIL' access.log
