class Solution {
    public int minMeetingRooms(List<Interval> intervals) {
        if (intervals.isEmpty()) return 0;

        intervals.sort((a, b) -> Integer.compare(a.start, b.start));

        PriorityQueue<Integer> rooms = new PriorityQueue<>();  // min-heap of end times

        for (Interval meeting : intervals) {
            // Reuse the room that ends earliest
            if (!rooms.isEmpty() && rooms.peek() <= meeting.start) rooms.poll();

            rooms.offer(meeting.end);
        }

        return rooms.size();
    }
}
