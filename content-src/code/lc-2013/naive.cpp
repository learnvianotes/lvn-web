class DetectSquares {
public:
    DetectSquares() {}

    void add(vector<int> point) {
        points[{point[0], point[1]}]++;
    }

    int count(vector<int> point) {
        int x = point[0], y = point[1];
        int answer = 0;

        for (auto& [p, cntDiag] : points) {
            auto [x2, y2] = p;
            if (x2 == x || y2 == y) {
                continue;
            }

            if (abs(x2 - x) != abs(y2 - y)) {
                continue;
            }

            answer += cntDiag * get(x2, y) * get(x, y2);
        }

        return answer;
    }

private:
    map<pair<int, int>, int> points;

    int get(int x, int y) {
        auto it = points.find({x, y});
        return it == points.end() ? 0 : it->second;
    }
};
