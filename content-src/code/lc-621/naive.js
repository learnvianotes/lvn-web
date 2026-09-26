var leastInterval = function(tasks, n) {
    const count = new Map();
    for (const task of tasks) count.set(task, (count.get(task) || 0) + 1);

    let time = 0;

    while (count.size > 0) {
        let executed = 0;

        // Sort by frequency each round
        const available = [...count.keys()].sort((a, b) => count.get(b) - count.get(a));

        for (const task of available.slice(0, n + 1)) {
            count.set(task, count.get(task) - 1);
            executed++;

            if (count.get(task) === 0) count.delete(task);
        }

        if (count.size > 0) time += n + 1;
        else time += executed;
    }

    return time;
};
