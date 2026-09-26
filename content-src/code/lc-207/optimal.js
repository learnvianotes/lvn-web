var canFinish = function(numCourses, prerequisites) {
    const graph = Array.from({ length: numCourses }, () => []);
    const indegree = new Array(numCourses).fill(0);

    for (const [course, prerequisite] of prerequisites) {
        graph[prerequisite].push(course);
        indegree[course]++;
    }

    const queue = [];
    for (let i = 0; i < numCourses; i++)
        if (indegree[i] === 0) queue.push(i);

    let completed = 0;

    for (let head = 0; head < queue.length; head++) {
        const course = queue[head];
        completed++;

        for (const next of graph[course])
            if (--indegree[next] === 0) queue.push(next);
    }

    return completed === numCourses;
};
