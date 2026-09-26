var findOrder = function(numCourses, prerequisites) {
    const graph = Array.from({ length: numCourses }, () => []);

    for (const [course, prerequisite] of prerequisites)
        graph[course].push(prerequisite);

    // 0 = unvisited, 1 = visiting, 2 = done
    const state = new Array(numCourses).fill(0);
    const result = [];

    const dfs = (course) => {
        if (state[course] === 1) return false;  // cycle
        if (state[course] === 2) return true;

        state[course] = 1;

        for (const prerequisite of graph[course])
            if (!dfs(prerequisite)) return false;

        state[course] = 2;
        result.push(course);  // after all its prerequisites

        return true;
    };

    for (let course = 0; course < numCourses; course++)
        if (!dfs(course)) return [];

    return result;
};
