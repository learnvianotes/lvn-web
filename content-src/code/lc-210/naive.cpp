class Solution {
public:
    vector<int> findOrder(int numCourses, vector<vector<int>>& prerequisites) {
        vector<vector<int>> graph(numCourses);

        for (auto& p : prerequisites)
            graph[p[0]].push_back(p[1]);

        // 0 = unvisited, 1 = visiting, 2 = done
        vector<int> state(numCourses, 0);
        vector<int> result;

        function<bool(int)> dfs = [&](int course) -> bool {
            if (state[course] == 1) return false;  // cycle
            if (state[course] == 2) return true;

            state[course] = 1;

            for (int prerequisite : graph[course])
                if (!dfs(prerequisite)) return false;

            state[course] = 2;
            result.push_back(course);  // after all its prerequisites

            return true;
        };

        for (int course = 0; course < numCourses; course++)
            if (!dfs(course)) return {};

        return result;
    }
};
