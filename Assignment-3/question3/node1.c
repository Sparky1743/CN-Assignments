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

int connectcosts1[4] = { 1,  0,  1, 999 };
int mincosts1[4]; // Minimum cost to each destination

struct distance_table 
{
  int costs[4][4];
} dt1;


/* students to write the following two routines, and maybe some others */


rtinit1() 
{
  printf("rtinit1 called at time %f\n", clocktime);
  
  // Initialize distance table with infinity (999)
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 4; j++) {
      dt1.costs[i][j] = 999;
    }
  }
  
  // Set costs to direct neighbors
  // For destination i via link i, set direct cost
  for (int i = 0; i < 4; i++) {
    dt1.costs[i][i] = connectcosts1[i];
    mincosts1[i] = connectcosts1[i]; // Initial min costs are direct costs
  }
  
  // Print initial distance table
  printf("Initial distance table for node 1:\n");
  printdt1(&dt1);
  
  // Create and send routing packets to neighbors (nodes 0 and 2)
  struct rtpkt packet;
  
  // Send to node 0
  creatertpkt(&packet, 1, 0, mincosts1);
  printf("Node 1 sending routing packet to node 0\n");
  tolayer2(packet);
  
  // Send to node 2
  creatertpkt(&packet, 1, 2, mincosts1);
  printf("Node 1 sending routing packet to node 2\n");
  tolayer2(packet);
}


rtupdate1(rcvdpkt)
  struct rtpkt *rcvdpkt;
  
{
  printf("rtupdate1 called at time %f, received packet from node %d\n", clocktime, rcvdpkt->sourceid);
  
  int sender = rcvdpkt->sourceid;
  int updated = NO;
  
  // Update distance table based on the received packet
  for (int i = 0; i < 4; i++) {
    dt1.costs[i][sender] = rcvdpkt->mincost[i] + connectcosts1[sender];
  }
  
  // Recalculate minimum costs
  for (int i = 0; i < 4; i++) {
    int oldmin = mincosts1[i];
    mincosts1[i] = 999;
    
    // Find minimum cost to destination i via any neighbor
    for (int j = 0; j < 4; j++) {
      if (dt1.costs[i][j] < mincosts1[i])
        mincosts1[i] = dt1.costs[i][j];
    }
    
    // Check if minimum cost changed
    if (mincosts1[i] != oldmin) {
      updated = YES;
    }
  }
  
  // Print updated distance table
  printf("Updated distance table for node 1:\n");
  printdt1(&dt1);
  
  // If minimum cost to any destination changed, send updates to neighbors
  if (updated == YES) {
    printf("Distance vector for node 1 changed, sending updates...\n");
    
    struct rtpkt packet;
    
    // Send to node 0
    creatertpkt(&packet, 1, 0, mincosts1);
    printf("Node 1 sending routing packet to node 0\n");
    tolayer2(packet);
    
    // Send to node 2
    creatertpkt(&packet, 1, 2, mincosts1);
    printf("Node 1 sending routing packet to node 2\n");
    tolayer2(packet);
  }
}


printdt1(dtptr)
  struct distance_table *dtptr;
  
{
  printf("             via   \n");
  printf("   D1 |    0     2 \n");
  printf("  ----|-----------\n");
  printf("     0|  %3d   %3d\n",dtptr->costs[0][0], dtptr->costs[0][2]);
  printf("dest 2|  %3d   %3d\n",dtptr->costs[2][0], dtptr->costs[2][2]);
  printf("     3|  %3d   %3d\n",dtptr->costs[3][0], dtptr->costs[3][2]);

}



linkhandler1(linkid, newcost)   
int linkid, newcost;   
/* called when cost from 1 to linkid changes from current value to newcost*/
/* You can leave this routine empty if you're an undergrad. If you want */
/* to use this routine, you'll need to change the value of the LINKCHANGE */
/* constant definition in prog3.c from 0 to 1 */
	
{
}


