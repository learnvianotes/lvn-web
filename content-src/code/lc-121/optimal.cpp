class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int minPrice = INT_MAX;
        int answer = 0;
        for (int price : prices) {
            minPrice = min(minPrice, price);
            answer = max(answer, price - minPrice);
        }
        return answer;
    }
};
