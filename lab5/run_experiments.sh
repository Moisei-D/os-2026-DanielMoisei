#!/usr/bin/env bash

set +e
export LC_ALL=C

LAB_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="$(mktemp -d "$LAB_DIR/experiment.XXXXXX")"

mkdir -p "$WORK_DIR"
cd "$WORK_DIR" || exit 1

cleanup_permissions() {
  chmod 755 box 2>/dev/null || true
  chmod 600 s.txt 2>/dev/null || true
}
trap cleanup_permissions EXIT

heading() {
  printf '\n===== %s =====\n' "$1"
}

run() {
  printf '\n$ %s\n' "$1"
  bash -c "$1" 2>&1
}

heading "Environment"
run "whoami"

heading "Part 1 - Tree and file types"
run "ls /"
run "ls -ld /etc /etc/passwd /bin /dev/null /tmp"
run "ls -l /dev | head"
run "file /usr/bin/ls /etc/passwd /bin"
run "du -sh /var/log 2>/dev/null ; du -sh /usr 2>/dev/null"

heading "Part 2 - Inodes and links"
run "echo hello > notes.txt"
run "stat notes.txt"
run "ls -li notes.txt"
run "ln notes.txt hard.txt"
run "ls -li notes.txt hard.txt"
run "rm notes.txt"
run "cat hard.txt ; ls -li hard.txt"
run "ln -s hard.txt soft.txt"
run "ls -li hard.txt soft.txt"
run "cat soft.txt"
run "rm hard.txt"
run "cat soft.txt ; ls -l soft.txt"
run "mkdir d ; ls -ld d"
run "mkdir d/x d/y ; ls -ld d"
run "echo x > one.txt ; ls -l one.txt ; du -h one.txt"
run "truncate -s 1G big.img ; ls -lh big.img ; du -h big.img"
run "rm big.img"

heading "Part 3 - Permissions"
run "echo secret > s.txt"
run "chmod 600 s.txt ; ls -l s.txt"
run "chmod 000 s.txt ; cat s.txt"
run "chmod u+r s.txt ; cat s.txt"
run "umask ; touch new.txt ; mkdir newdir ; ls -ld new.txt newdir"
run "mkdir box ; echo hi > box/f"
run "chmod u=r,go= box ; ls box ; cat box/f"
run "chmod u=x,go= box ; ls box ; cat box/f"
run "chmod 755 box"
run "ls -l /usr/bin/passwd ; ls -ld /tmp"
run "cat /etc/shadow"
run "ls -l /etc/shadow"

heading "Part 4 - Disks and the kernel as files"
run "lsblk -o NAME,MAJ:MIN,RM,SIZE,RO,TYPE,FSTYPE,MOUNTPOINTS"
run "df -hT /"
run "mount | grep ' / '"
run "grep -c processor /proc/cpuinfo"
run "head -3 /proc/meminfo"
run "head -5 /proc/self/status"
run "ls -l /proc/self/fd"

heading "Stretch - Magic numbers"
run "gzip -c /etc/passwd > compressed-notes.txt"
run "file compressed-notes.txt"
run "od -An -tx1 -N16 compressed-notes.txt"

