#define _GNU_SOURCE
#define _FILE_OFFSET_BITS 64
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/resource.h>

#define errExit(msg) do { perror(msg); exit(EXIT_FAILURE); \
 } while (0)

int
main(int argc, char *argv[])
{
 struct rlimit old, new, old2, new2;
 struct rlimit *newp, *newp2;
 pid_t pid;

 if (!(argc == 2 || argc == 4)) {
 fprintf(stderr, "Usage: %s <pid> [<new-soft-limit> "
 "<new-hard-limit>]\n", argv[0]);
 exit(EXIT_FAILURE);
 }

 pid = atoi(argv[1]); /* PID of target process */

 newp = NULL;
 if (argc == 4) {
 new.rlim_cur = atoi(argv[2]);
 new.rlim_max = atoi(argv[3]);
 newp = &new;

 }

 if (prlimit(pid, RLIMIT_NOFILE, newp, &old) == -1)
 errExit("prlimit-1");
 printf("Previous limits NOFILE: soft=%lld; hard=%lld\n",
 (long long) old.rlim_cur, (long long) old.rlim_max);

 if (prlimit(pid, RLIMIT_NOFILE, NULL, &old) == -1)
 errExit("prlimit-2");
 printf("New limits NOFILE: soft=%lld; hard=%lld\n",
 (long long) old.rlim_cur, (long long) old.rlim_max);


 new2.rlim_cur = (atoi(argv[2])/2);
 new2.rlim_max = (atoi(argv[3])/2);
 newp2 = &new2;

 if (prlimit(pid, RLIMIT_NPROC, newp2, &old2) == -1)
 errExit("prlimit-1");
 printf("Previous limits PROC: soft=%lld; hard=%lld\n",
 (long long) old2.rlim_cur, (long long) old2.rlim_max);

 if (prlimit(pid, RLIMIT_NPROC, NULL, &old2) == -1)
 errExit("prlimit-2");
 printf("New limits PROC: soft=%lld; hard=%lld\n",
 (long long) old2.rlim_cur, (long long) old2.rlim_max);

 exit(EXIT_FAILURE);
}
