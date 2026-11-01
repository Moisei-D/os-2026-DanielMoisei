#include "kernel/types.h"
#include "user/user.h"

void stage(int fd) __attribute__((noreturn));

// one stage of the prime sieve: read from fd, print the first number,
// forward the numbers not divisible by it to the next stage
void
stage(int fd)
{
  int p, n;
  if(read(fd, &p, sizeof(p)) <= 0){
    close(fd);
    exit(0);
  }
  printf("prime %d\n", p);

  int next[2];
  pipe(next);
  if(fork() == 0){
    close(next[1]);
    close(fd);
    stage(next[0]);
  }
  close(next[0]);
  while(read(fd, &n, sizeof(n)) > 0){
    if(n % p != 0)
      write(next[1], &n, sizeof(n));
  }
  close(fd);
  close(next[1]);
  wait(0);
  exit(0);
}

int
main(int argc, char *argv[])
{
  int first[2];
  pipe(first);
  if(fork() == 0){
    close(first[1]);
    stage(first[0]);
  }
  close(first[0]);
  for(int i = 2; i <= 35; i++)
    write(first[1], &i, sizeof(i));
  close(first[1]);
  wait(0);
  exit(0);
}
