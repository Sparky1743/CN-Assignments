# Creating a Convergence Graph in Excel/Google Sheets

1. Extract the following data points from your simulation output:
   - Simulation time
   - Updated minimum costs for each node

2. Create a table with the following columns:
   - Time
   - Node 0 to Node 1 cost
   - Node 0 to Node 2 cost
   - Node 0 to Node 3 cost

3. Fill the table with data from the simulation output:
   ```
   Time    | 0→1 | 0→2 | 0→3
   --------|-----|-----|-----
   0.000   |  1  |  3  |  7
   0.992   |  1  |  2  |  7
   4.103   |  1  |  2  |  7
   5.212   |  1  |  2  |  7
   6.071   |  1  |  2  |  7
   7.405   |  1  |  2  |  4
   ```

4. Create a scatter plot with smooth lines:
   - X-axis: Time
   - Y-axis: Cost
   - Create separate series for each destination node

5. Add appropriate titles and labels:
   - Title: "Distance Vector Algorithm Convergence"
   - X-axis label: "Simulation Time"
   - Y-axis label: "Minimum Cost"
   - Legend: "Node 0 to Node X"
