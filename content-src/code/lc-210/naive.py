class Solution:
    def findOrder(self, numCourses, prerequisites):
        graph = [[] for _ in range(numCourses)]

        for course, prerequisite in prerequisites:
            graph[course].append(prerequisite)

        # 0 = unvisited, 1 = visiting, 2 = done
        state = [0] * numCourses
        result = []

        def dfs(course):
            if state[course] == 1:
                return False  # cycle

            if state[course] == 2:
                return True

            state[course] = 1

            for prerequisite in graph[course]:
                if not dfs(prerequisite):
                    return False

            state[course] = 2
            result.append(course)  # after all its prerequisites

            return True

        for course in range(numCourses):
            if not dfs(course):
                return []

        return result
