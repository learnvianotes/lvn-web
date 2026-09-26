class Solution {
    public int findCheapestPrice(int n, int[][] flights, int src, int dst, int k) {
        final int INF = Integer.MAX_VALUE;
        int[] prices = new int[n];
        Arrays.fill(prices, INF);
        prices[src] = 0;

        for (int i = 0; i <= k; i++) {
            int[] tmp = prices.clone();

            for (int[] f : flights) {
                int u = f[0], v = f[1], price = f[2];

                if (prices[u] == INF) continue;

                if (prices[u] + price < tmp[v])
                    tmp[v] = prices[u] + price;
            }

            prices = tmp;
        }

        return prices[dst] != INF ? prices[dst] : -1;
    }
}
