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
} dt2;

// Connection costs for Node 2
int connectcosts2[4] = { 3, 1, 0, 2 };
int mincosts2[4]; // Minimum cost to each destination

/* students to write the following two routines, and maybe some others */

void rtinit2() 
{
  printf("rtinit2 called at time %f\n", clocktime);
  
  // Initialize distance table with infinity (999)
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 4; j++) {
      dt2.costs[i][j] = 999;
    }
  }
  
  // Set costs to direct neighbors
  // For destination i via link i, set direct cost
  for (int i = 0; i < 4; i++) {
    dt2.costs[i][i] = connectcosts2[i];
    mincosts2[i] = connectcosts2[i]; // Initial min costs are direct costs
  }
  
  // Print initial distance table
  printf("Initial distance table for node 2:\n");
  printdt2(&dt2);
  
  // Create and send routing packets to neighbors (nodes 0, 1, and 3)
  struct rtpkt packet;
  
  // Send to node 0
  creatertpkt(&packet, 2, 0, mincosts2);
  printf("Node 2 sending routing packet to node 0\n");
  tolayer2(packet);
  
  // Send to node 1
  creatertpkt(&packet, 2, 1, mincosts2);
  printf("Node 2 sending routing packet to node 1\n");
  tolayer2(packet);
  
  // Send to node 3
  creatertpkt(&packet, 2, 3, mincosts2);
  printf("Node 2 sending routing packet to node 3\n");
  tolayer2(packet);
}


void rtupdate2(rcvdpkt)
  struct rtpkt *rcvdpkt;
  
{
  printf("rtupdate2 called at time %f, received packet from node %d\n", clocktime, rcvdpkt->sourceid);
  
  int sender = rcvdpkt->sourceid;
  int updated = NO;
  
  // Update distance table based on the received packet
  for (int i = 0; i < 4; i++) {
    dt2.costs[i][sender] = rcvdpkt->mincost[i] + connectcosts2[sender];
  }
  
  // Recalculate minimum costs
  for (int i = 0; i < 4; i++) {
    int oldmin = mincosts2[i];
    mincosts2[i] = 999;
    
    // Find minimum cost to destination i via any neighbor
    for (int j = 0; j < 4; j++) {
      if (dt2.costs[i][j] < mincosts2[i])
        mincosts2[i] = dt2.costs[i][j];
    }
    
    // Check if minimum cost changed
    if (mincosts2[i] != oldmin) {
      updated = YES;
    }
  }
  
  // Print updated distance table
  printf("Updated distance table for node 2:\n");
  printdt2(&dt2);
  
  // If minimum cost to any destination changed, send updates to neighbors
  if (updated == YES) {
    printf("Distance vector for node 2 changed, sending updates...\n");
    
    struct rtpkt packet;
    
    // Send to node 0
    creatertpkt(&packet, 2, 0, mincosts2);
    printf("Node 2 sending routing packet to node 0\n");
    tolayer2(packet);
    
    // Send to node 1
    creatertpkt(&packet, 2, 1, mincosts2);
    printf("Node 2 sending routing packet to node 1\n");
    tolayer2(packet);
    
    // Send to node 3
    creatertpkt(&packet, 2, 3, mincosts2);
    printf("Node 2 sending routing packet to node 3\n");
    tolayer2(packet);
  }
}


printdt2(dtptr)
  struct distance_table *dtptr;
  
{
  printf("                via     \n");
  printf("   D2 |    0     1    3 \n");
  printf("  ----|-----------------\n");
  printf("     0|  %3d   %3d   %3d\n",dtptr->costs[0][0],
	 dtptr->costs[0][1],dtptr->costs[0][3]);
  printf("dest 1|  %3d   %3d   %3d\n",dtptr->costs[1][0],
	 dtptr->costs[1][1],dtptr->costs[1][3]);
  printf("     3|  %3d   %3d   %3d\n",dtptr->costs[3][0],
	 dtptr->costs[3][1],dtptr->costs[3][3]);
}







