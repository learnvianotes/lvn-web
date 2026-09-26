class Solution {
public:
    int findCheapestPrice(int n, vector<vector<int>>& flights, int src, int dst, int k) {
        const int INF = INT_MAX;
        vector<int> prices(n, INF);
        prices[src] = 0;

        for (int i = 0; i <= k; i++) {
            vector<int> tmp = prices;

            for (auto& f : flights) {
                int u = f[0], v = f[1], price = f[2];

                if (prices[u] == INF) continue;

                if (prices[u] + price < tmp[v])
                    tmp[v] = prices[u] + price;
            }

            prices = tmp;
        }

        return prices[dst] != INF ? prices[dst] : -1;
    }
};
