var minMeetingRooms = function(intervals) {
    let answer = 0;

    for (const { start } of intervals) {
        let rooms = 0;

        for (const other of intervals) {
            if (other.start <= start && start < other.end) rooms++;
        }

        answer = Math.max(answer, rooms);
    }

    return answer;
};
