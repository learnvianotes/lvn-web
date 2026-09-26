class Solution {
public:
    int carFleet(int target, vector<int>& position, vector<int>& speed) {
        vector<pair<int, int>> cars;
        for (int i = 0; i < position.size(); i++) cars.push_back({position[i], speed[i]});
        sort(cars.begin(), cars.end());
        vector<double> fleets;
        for (auto& [pos, spd] : cars) {
            double time = (double)(target - pos) / spd;
            while (!fleets.empty() && fleets.back() <= time) fleets.pop_back();
            fleets.push_back(time);
        }
        return fleets.size();
    }
};
