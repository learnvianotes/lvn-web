class DetectSquares {
public:
    DetectSquares() {}

    void add(vector<int> point) {
        int x = point[0], y = point[1];
        points[x][y]++;
    }

    int count(vector<int> point) {
        int x = point[0], y = point[1];
        int answer = 0;

        for (auto& [x2, ys] : points) {
            if (x2 == x) {
                continue;
            }

            int side = abs(x2 - x);

            // Two possible diagonal y-coords
            for (int y2 : {y + side, y - side}) {
                auto it = ys.find(y2);
                if (it == ys.end()) {
                    continue;
                }

                int cntDiag   = it->second;     // (x2, y2)
                int cntCorner = get(x, y2);     // (x,  y2)
                int cntBase   = get(x2, y);     // (x2, y )

                answer += cntDiag * cntCorner * cntBase;
            }
        }

        return answer;
    }

private:
    // points[x][y] = frequency
    unordered_map<int, unordered_map<int, int>> points;

    // lookup without inserting (inserting would invalidate the loop's iterators)
    int get(int x, int y) {
        auto row = points.find(x);
        if (row == points.end()) return 0;
        auto it = row->second.find(y);
        return it == row->second.end() ? 0 : it->second;
    }
};
