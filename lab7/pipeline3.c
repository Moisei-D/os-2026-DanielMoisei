#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

/* does the same as the shell command:   ls /usr/bin | grep x | wc -l   */
int main(void)
{
    int p[2], q[2];
    if (pipe(p) < 0 || pipe(q) < 0) { perror("pipe"); return 1; }

    if (fork() == 0) {                          /* ls: 1 -> p[1] */
        close(1); dup(p[1]);
        close(p[0]); close(p[1]); close(q[0]); close(q[1]);
        execlp("ls", "ls", "/usr/bin", (char *)NULL);
        perror("exec ls"); exit(127);
    }
    if (fork() == 0) {                          /* grep: 0 <- p[0], 1 -> q[1] */
        close(0); dup(p[0]);
        close(1); dup(q[1]);
        close(p[0]); close(p[1]); close(q[0]); close(q[1]);
        execlp("grep", "grep", "x", (char *)NULL);
        perror("exec grep"); exit(127);
    }
    if (fork() == 0) {                          /* wc: 0 <- q[0] */
        close(0); dup(q[0]);
        close(p[0]); close(p[1]); close(q[0]); close(q[1]);
        execlp("wc", "wc", "-l", (char *)NULL);
        perror("exec wc"); exit(127);
    }

    close(p[0]); close(p[1]); close(q[0]); close(q[1]);
    wait(NULL); wait(NULL); wait(NULL);
    return 0;
}
