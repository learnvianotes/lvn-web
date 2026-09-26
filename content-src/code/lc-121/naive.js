var maxProfit = function(prices) {
    let answer = 0;
    for (let i = 0; i < prices.length; i++)
        for (let j = i + 1; j < prices.length; j++)
            answer = Math.max(answer, prices[j] - prices[i]);
    return answer;
};
