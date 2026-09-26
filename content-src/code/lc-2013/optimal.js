var DetectSquares = function() {
    // points.get(x).get(y) = frequency
    this.points = new Map();
};

DetectSquares.prototype.add = function(point) {
    const [x, y] = point;
    if (!this.points.has(x)) {
        this.points.set(x, new Map());
    }
    const ys = this.points.get(x);
    ys.set(y, (ys.get(y) || 0) + 1);
};

DetectSquares.prototype.count = function(point) {
    const [x, y] = point;
    const get = (px, py) => this.points.get(px)?.get(py) || 0;
    let answer = 0;

    for (const [x2, ys] of this.points) {
        if (x2 === x) {
            continue;
        }

        const side = Math.abs(x2 - x);

        // Two possible diagonal y-coords
        for (const y2 of [y + side, y - side]) {
            if (!ys.has(y2)) {
                continue;
            }

            const cntDiag   = ys.get(y2);    // (x2, y2)
            const cntCorner = get(x, y2);    // (x,  y2)
            const cntBase   = get(x2, y);    // (x2, y )

            answer += cntDiag * cntCorner * cntBase;
        }
    }

    return answer;
};
