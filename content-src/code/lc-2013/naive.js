var DetectSquares = function() {
    this.points = new Map();  // "x,y" -> frequency
};

DetectSquares.prototype.add = function(point) {
    const key = point.join(",");
    this.points.set(key, (this.points.get(key) || 0) + 1);
};

DetectSquares.prototype.count = function(point) {
    const [x, y] = point;
    let answer = 0;

    for (const [key, cntDiag] of this.points) {
        const [x2, y2] = key.split(",").map(Number);
        if (x2 === x || y2 === y) {
            continue;
        }

        if (Math.abs(x2 - x) !== Math.abs(y2 - y)) {
            continue;
        }

        answer +=
            cntDiag *
            (this.points.get(`${x2},${y}`) || 0) *
            (this.points.get(`${x},${y2}`) || 0);
    }

    return answer;
};
