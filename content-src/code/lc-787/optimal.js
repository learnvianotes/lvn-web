var findCheapestPrice = function(n, flights, src, dst, k) {
    let prices = new Array(n).fill(Infinity);
    prices[src] = 0;

    for (let i = 0; i <= k; i++) {
        const tmp = [...prices];

        for (const [u, v, price] of flights) {
            if (prices[u] === Infinity) continue;

            if (prices[u] + price < tmp[v]) tmp[v] = prices[u] + price;
        }

        prices = tmp;
    }

    return prices[dst] !== Infinity ? prices[dst] : -1;
};
