class Solution {
    public int minMeetingRooms(List<Interval> intervals) {
        int answer = 0;

        for (Interval meeting : intervals) {
            int rooms = 0;

            for (Interval other : intervals) {
                if (other.start <= meeting.start && meeting.start < other.end) rooms++;
            }

            answer = Math.max(answer, rooms);
        }

        return answer;
    }
}
