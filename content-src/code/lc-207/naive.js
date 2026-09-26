var canFinish = function(numCourses, prerequisites) {
    const graph = Array.from({ length: numCourses }, () => []);

    for (const [course, prerequisite] of prerequisites)
        graph[course].push(prerequisite);

    const visiting = new Set();
    const visited = new Set();

    const dfs = (course) => {
        if (visiting.has(course)) return false;
        if (visited.has(course)) return true;

        visiting.add(course);

        for (const prerequisite of graph[course])
            if (!dfs(prerequisite)) return false;

        visiting.delete(course);
        visited.add(course);

        return true;
    };

    for (let course = 0; course < numCourses; course++)
        if (!dfs(course)) return false;

    return true;
};
