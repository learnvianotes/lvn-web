class Solution:
    def minMeetingRooms(self, intervals):
        answer = 0

        for start, _ in intervals:
            rooms = 0

            for other_start, other_end in intervals:
                if other_start <= start < other_end:
                    rooms += 1

            answer = max(answer, rooms)

        return answer