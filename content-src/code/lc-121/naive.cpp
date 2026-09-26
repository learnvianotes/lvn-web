class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int answer = 0;
        for (int i = 0; i < prices.size(); i++)
            for (int j = i + 1; j < prices.size(); j++)
                answer = max(answer, prices[j] - prices[i]);
        return answer;
    }
};
