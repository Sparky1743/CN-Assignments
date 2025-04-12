#include <stdio.h>

extern struct rtpkt {
  int sourceid;       /* id of sending router sending this pkt */
  int destid;         /* id of router to which pkt being sent 
                         (must be an immediate neighbor) */
  int mincost[4];    /* min cost to node 0 ... 3 */
  };

extern float clocktime; 
extern int TRACE;
extern int YES;
extern int NO;

struct distance_table 
{
  int costs[4][4];
} dt0;

// Connection costs for Node 0
int connectcosts0[4] = { 0, 1, 3, 7 };
int mincosts0[4]; // Minimum cost to each destination
/* students to write the following two routines, and maybe some others */

void rtinit0() 
{
  printf("rtinit0 called at time %f\n", clocktime);
  
  // Initialize distance table with infinity (999)
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 4; j++) {
      dt0.costs[i][j] = 999;
    }
  }
  
  // Set costs to direct neighbors
  // For destination i via link i, set direct cost
  for (int i = 0; i < 4; i++) {
    dt0.costs[i][i] = connectcosts0[i];
    mincosts0[i] = connectcosts0[i]; // Initial min costs are direct costs
  }
  
  // Print initial distance table
  printf("Initial distance table for node 0:\n");
  printdt0(&dt0);
  
  // Create and send routing packets to neighbors (nodes 1, 2, and 3)
  struct rtpkt packet;
  
  // Send to node 1
  creatertpkt(&packet, 0, 1, mincosts0);
  printf("Node 0 sending routing packet to node 1\n");
  tolayer2(packet);
  
  // Send to node 2
  creatertpkt(&packet, 0, 2, mincosts0);
  printf("Node 0 sending routing packet to node 2\n");
  tolayer2(packet);
  
  // Send to node 3
  creatertpkt(&packet, 0, 3, mincosts0);
  printf("Node 0 sending routing packet to node 3\n");
  tolayer2(packet);
}


void rtupdate0(rcvdpkt)
  struct rtpkt *rcvdpkt;
{
  printf("rtupdate0 called at time %f, received packet from node %d\n", clocktime, rcvdpkt->sourceid);
  
  int sender = rcvdpkt->sourceid;
  int updated = NO;
  
  // Update distance table based on the received packet
  for (int i = 0; i < 4; i++) {
    dt0.costs[i][sender] = rcvdpkt->mincost[i] + connectcosts0[sender];
  }
  
  // Recalculate minimum costs
  for (int i = 0; i < 4; i++) {
    int oldmin = mincosts0[i];
    mincosts0[i] = 999;
    
    // Find minimum cost to destination i via any neighbor
    for (int j = 0; j < 4; j++) {
      if (dt0.costs[i][j] < mincosts0[i])
        mincosts0[i] = dt0.costs[i][j];
    }
    
    // Check if minimum cost changed
    if (mincosts0[i] != oldmin) {
      updated = YES;
    }
  }
  
  // Print updated distance table
  printf("Updated distance table for node 0:\n");
  printdt0(&dt0);
  
  // If minimum cost to any destination changed, send updates to neighbors
  if (updated == YES) {
    printf("Distance vector for node 0 changed, sending updates...\n");
    
    struct rtpkt packet;
    
    // Send to node 1
    creatertpkt(&packet, 0, 1, mincosts0);
    printf("Node 0 sending routing packet to node 1\n");
    tolayer2(packet);
    
    // Send to node 2
    creatertpkt(&packet, 0, 2, mincosts0);
    printf("Node 0 sending routing packet to node 2\n");
    tolayer2(packet);
    
    // Send to node 3
    creatertpkt(&packet, 0, 3, mincosts0);
    printf("Node 0 sending routing packet to node 3\n");
    tolayer2(packet);
  }
}


printdt0(dtptr)
  struct distance_table *dtptr;
  
{
  printf("                via     \n");
  printf("   D0 |    1     2    3 \n");
  printf("  ----|-----------------\n");
  printf("     1|  %3d   %3d   %3d\n",dtptr->costs[1][1],
	 dtptr->costs[1][2],dtptr->costs[1][3]);
  printf("dest 2|  %3d   %3d   %3d\n",dtptr->costs[2][1],
	 dtptr->costs[2][2],dtptr->costs[2][3]);
  printf("     3|  %3d   %3d   %3d\n",dtptr->costs[3][1],
	 dtptr->costs[3][2],dtptr->costs[3][3]);
}

linkhandler0(linkid, newcost)   
  int linkid, newcost;

/* called when cost from 0 to linkid changes from current value to newcost*/
/* You can leave this routine empty if you're an undergrad. If you want */
/* to use this routine, you'll need to change the value of the LINKCHANGE */
/* constant definition in prog3.c from 0 to 1 */
	
{
}

