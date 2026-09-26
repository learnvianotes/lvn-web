class Solution:
    def solve(self, board):
        rows = len(board)
        cols = len(board[0])

        # Can this 'O' reach the border through other 'O's?
        def reaches_border(r, c, visited):
            if r < 0 or r >= rows or c < 0 or c >= cols:
                return True

            if board[r][c] != "O" or (r, c) in visited:
                return False

            visited.add((r, c))

            return (
                reaches_border(r + 1, c, visited)
                or reaches_border(r - 1, c, visited)
                or reaches_border(r, c + 1, visited)
                or reaches_border(r, c - 1, visited)
            )

        for r in range(rows):
            for c in range(cols):
                if board[r][c] != "O":
                    continue

                if not reaches_border(r, c, set()):
                    board[r][c] = "X"
