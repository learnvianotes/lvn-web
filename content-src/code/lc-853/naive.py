class Solution:
    def carFleet(self, target, position, speed):

        cars = sorted(
            zip(position, speed)
        )

        fleets = []

        for pos, spd in cars:
            time = (target - pos) / spd

            while (
                fleets
                and fleets[-1] <= time
            ):
                fleets.pop()

            fleets.append(time)

        return len(fleets)