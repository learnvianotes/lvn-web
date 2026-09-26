var findItinerary = function(tickets) {
    const graph = new Map();

    // reverse lexical order, so pop() yields the smallest destination
    const sorted = [...tickets].sort((a, b) =>
        a[0] === b[0] ? (a[1] < b[1] ? 1 : a[1] > b[1] ? -1 : 0)
                      : (a[0] < b[0] ? 1 : -1));

    for (const [src, dst] of sorted) {
        if (!graph.has(src)) graph.set(src, []);
        graph.get(src).push(dst);
    }

    const itinerary = [];

    const dfs = (airport) => {
        const destinations = graph.get(airport) || [];

        while (destinations.length) {
            dfs(destinations.pop());
        }

        itinerary.push(airport);
    };

    dfs("JFK");
    return itinerary.reverse();
};
