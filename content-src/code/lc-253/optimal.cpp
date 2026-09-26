class Solution {
public:
    int minMeetingRooms(vector<Interval>& intervals) {
        if (intervals.empty()) return 0;

        sort(intervals.begin(), intervals.end(), [](const Interval& a, const Interval& b) {
            return a.start < b.start;
        });

        priority_queue<int, vector<int>, greater<int>> rooms;  // min-heap of end times

        for (auto& meeting : intervals) {
            // Reuse the room that ends earliest
            if (!rooms.empty() && rooms.top() <= meeting.start) rooms.pop();

            rooms.push(meeting.end);
        }

        return rooms.size();
    }
};
