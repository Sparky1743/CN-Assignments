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
} dt3;

// Connection costs for Node 3
int connectcosts3[4] = { 7, 999, 2, 0 };
int mincosts3[4]; // Minimum cost to each destination

void rtinit3() 
{
  printf("rtinit3 called at time %f\n", clocktime);
  
  // Initialize distance table with infinity (999)
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 4; j++) {
      dt3.costs[i][j] = 999;
    }
  }
  
  // Set costs to direct neighbors
  // For destination i via link i, set direct cost
  for (int i = 0; i < 4; i++) {
    dt3.costs[i][i] = connectcosts3[i];
    mincosts3[i] = connectcosts3[i]; // Initial min costs are direct costs
  }
  
  // Print initial distance table
  printf("Initial distance table for node 3:\n");
  printdt3(&dt3);
  
  // Create and send routing packets to neighbors (nodes 0 and 2)
  struct rtpkt packet;
  
  // Send to node 0
  creatertpkt(&packet, 3, 0, mincosts3);
  printf("Node 3 sending routing packet to node 0\n");
  tolayer2(packet);
  
  // Send to node 2
  creatertpkt(&packet, 3, 2, mincosts3);
  printf("Node 3 sending routing packet to node 2\n");
  tolayer2(packet);
}


void rtupdate3(rcvdpkt)
  struct rtpkt *rcvdpkt;
  
{
  printf("rtupdate3 called at time %f, received packet from node %d\n", clocktime, rcvdpkt->sourceid);
  
  int sender = rcvdpkt->sourceid;
  int updated = NO;
  
  // Update distance table based on the received packet
  for (int i = 0; i < 4; i++) {
    dt3.costs[i][sender] = rcvdpkt->mincost[i] + connectcosts3[sender];
  }
  
  // Recalculate minimum costs
  for (int i = 0; i < 4; i++) {
    int oldmin = mincosts3[i];
    mincosts3[i] = 999;
    
    // Find minimum cost to destination i via any neighbor
    for (int j = 0; j < 4; j++) {
      if (dt3.costs[i][j] < mincosts3[i])
        mincosts3[i] = dt3.costs[i][j];
    }
    
    // Check if minimum cost changed
    if (mincosts3[i] != oldmin) {
      updated = YES;
    }
  }
  
  // Print updated distance table
  printf("Updated distance table for node 3:\n");
  printdt3(&dt3);
  
  // If minimum cost to any destination changed, send updates to neighbors
  if (updated == YES) {
    printf("Distance vector for node 3 changed, sending updates...\n");
    
    struct rtpkt packet;
    
    // Send to node 0
    creatertpkt(&packet, 3, 0, mincosts3);
    printf("Node 3 sending routing packet to node 0\n");
    tolayer2(packet);
    
    // Send to node 2
    creatertpkt(&packet, 3, 2, mincosts3);
    printf("Node 3 sending routing packet to node 2\n");
    tolayer2(packet);
  }
}


printdt3(dtptr)
  struct distance_table *dtptr;
  
{
  printf("             via     \n");
  printf("   D3 |    0     2 \n");
  printf("  ----|-----------\n");
  printf("     0|  %3d   %3d\n",dtptr->costs[0][0], dtptr->costs[0][2]);
  printf("dest 1|  %3d   %3d\n",dtptr->costs[1][0], dtptr->costs[1][2]);
  printf("     2|  %3d   %3d\n",dtptr->costs[2][0], dtptr->costs[2][2]);

}







