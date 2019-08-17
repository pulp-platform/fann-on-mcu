#include <stdio.h>
#include <stdlib.h>
#include <pulp.h>
#include "cluster.h"



int main(int argc, char *argv[])
{
    printf("starting tests....\n");

  // Before being used, the cluster must be mounter, for example in case it must be
  // turned on.
  rt_cluster_mount(1, 0, 0, NULL);
  
  // This is the most basic call we can do to the cluster with all default
  // parameters (default stack size, max number of cores, etc) and is 
  // synchronous (last event parameter is NULL) which means we are blocked
  // until the call is finished
  rt_cluster_call(NULL, 0, cluster_entry, NULL, NULL, 0x400, 0x200, 0, NULL);

  // It must then be unmounted when it is not needed anymore so that it is turned off
  rt_cluster_mount(0, 0, 0, NULL);

    printf("ending tests....\n");

    return 0;
    
}
