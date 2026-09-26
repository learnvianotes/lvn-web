class Solution {
public:
    int minMeetingRooms(vector<Interval>& intervals) {
        int answer = 0;

        for (auto& meeting : intervals) {
            int rooms = 0;

            for (auto& other : intervals) {
                if (other.start <= meeting.start && meeting.start < other.end) rooms++;
            }

            answer = max(answer, rooms);
        }

        return answer;
    }
};
