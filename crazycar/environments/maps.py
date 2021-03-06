import math
import crazycar
import os


MODULE_PATH = os.path.dirname(os.path.abspath(crazycar.__file__))


class Map:

    def __init__(self, p, origin):
        self.p = p
        self.width = 0.05
        self.x = origin[0] + 2.9 / 2
        self.y = origin[1] - self.width / 2.0
        self.z = origin[2] + 0.1
        self.d = 0.2545
        self.Orientation000 = p.getQuaternionFromEuler([0, 0, 0])
        self.Orientation045 = p.getQuaternionFromEuler([0, 0, math.pi / 4])
        self.Orientation090 = p.getQuaternionFromEuler([0, 0, math.pi / 2])
        self.Orientation135 = p.getQuaternionFromEuler([0, 0, -math.pi / 4])
        self.map = {
            1: self.map1,
            2: self.map2
        }

    def map1(self):
        w1 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem2900.urdf"),
            [self.x, self.y, self.z],
            self.Orientation000
        )
        w2 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem6500.urdf"),
            [self.x + 2.9 / 2 - self.width / 2, self.y + 6.5 / 2 + self.width / 2, self.z],
            self.Orientation090
        )
        w3 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem2900.urdf"),
            [self.x - self.width, self.y + 6.5, self.z],
            self.Orientation000
        )
        w4 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem6500.urdf"),
            [self.x - 2.9 / 2 - self.width / 2, self.y + 6.5 / 2 - self.width / 2, self.z],
            self.Orientation090
        )

        # inside1
        os.path.join(MODULE_PATH, "data/elem0200.urdf")
        os.path.join(MODULE_PATH, "data/elem0800.urdf")
        os.path.join(MODULE_PATH, "data/elem1400-1.urdf")
        os.path.join(MODULE_PATH, "data/elem5000.urdf")
        w5 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem0200.urdf"),
            [self.x - 1.4 / 2 - self.width, self.y + 0.7 + 0.8 + self.width / 2, self.z],
            self.Orientation000
        )
        w6 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem0800.urdf"),
            [self.x - 1.4 / 2 + self.width / 2, self.y + 0.7 + 0.8 / 2, self.z],
            self.Orientation090
        )
        w7 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem1400-1.urdf"),
            [self.x + self.width, self.y + 0.7 + self.width / 2, self.z],
            self.Orientation000
        )
        w8 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem5000.urdf"),
            [self.x + self.width - self.width / 2 + 1.4 / 2, self.y + 0.7 + self.width + 5.0 / 2, self.z],
            self.Orientation090
        )
        w9 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem1400-1.urdf"),
            [self.x + self.width - self.width, self.y + 0.7 + self.width / 2 + 5.0, self.z],
            self.Orientation000
        )
        w10 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem2000.urdf"),
            [self.x + self.width - self.width / 2 - 0.7, self.y + 0.7 + 5.0 - 2 / 2, self.z],
            self.Orientation090
        )
        # inside2
        w11 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem2600.urdf"),
            [self.x - 2.9 / 2 + 1.4 + self.width / 2, self.y + 0.7 + self.width \
                + 5.0 - self.width - 0.78 - 2.6 / 2, self.z],
            self.Orientation090
        )
        w12 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem1400-1.urdf"),
            [self.x - 2.9 / 2 + 1.4 / 2, self.y + 0.7 + self.width / 2 + 5.0 - 2.6 / 2 - 0.78 - 2.6 / 2, self.z],
            self.Orientation000
        )

        # corners
        w13 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem0720.urdf"),
            [self.x + self.width + 1.4 / 2 - self.d - self.width / 2, self.y + 0.7 + self.width / 2 + self.d, self.z],
            self.Orientation045
        )
        w14 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem0720.urdf"),
            [self.x + self.width - 1.4 / 2 + self.d - self.width / 2, self.y + 0.7 + self.width / 2 + self.d, self.z],
            self.Orientation135
        )

        x1 = 2.9 / 2 - 1.4 / 2 + 0.05 / 2
        x2 = 2.9 / 2 - 2.9 / 2 + 1.4 + 0.05 / 2
        x3 = 2.9 / 2 + 0.05 - 0.05 / 2 + 1.4 / 2
        x4 = 2.9 - 0.05 / 2

        y1 = -0.05 / 2 + 0.7 + 0.05 / 2
        y2 = -0.05 / 2 + 0.7 + 0.05 / 2 + 5.0 - 2.6 / 2 - 0.78 - 2.6 / 2
        y3 = -0.05 / 2 + 0.7 + 5.0 - 2 + 0.05 / 2
        y4 = -0.05 / 2 + 0.7 + 0.05 + 5.0 - 0.78 - 0.05
        y5 = -0.05 / 2 + 0.7 + 0.05 / 2 + 5
        y6 = -0.05 / 2 + 6.5

        direction_field = [
            # 0
            lambda i, j: "0" if (x1 <= i <= x3) and (0 <= j <= y1) else None,

            # 45
            lambda i, j: "45" if (x3 <= i <= x4) and (0 <= j <= y1) else None,
            lambda i, j: "45" if (x1 <= i <= x2) and (y2 <= j <= y3) else None,
            lambda i, j: "45" if (x1 <= i <= x2) and (y4 <= j <= y5) else None,

            # 90
            lambda i, j: "90" if (x3 <= i <= x4) and (y1 <= j <= y5) else None,
            lambda i, j: "90" if (x1 <= i <= x2) and (y3 <= j <= y4) else None,

            # 135
            lambda i, j: "135" if (x3 <= i <= x4) and (y5 <= j <= y6) else None,

            # 180
            lambda i, j: "180" if (x1 <= i <= x3) and (y1 <= j <= y2) else None,
            lambda i, j: "180" if (x1 <= i <= x3) and (y5 <= j <= y6) else None,

            # -135
            lambda i, j: "-135" if (0 <= i <= x1) and (y5 <= j <= y6) else None,
            lambda i, j: "-135" if (0 <= i <= x1) and ((y1 + y2) / 2 <= j <= y2) else None,

            # -90
            lambda i, j: "-90" if (0 <= i <= x1) and (y1 <= j <= (y1 + y2) / 2) else None,
            lambda i, j: "-90" if (0 <= i <= x1) and (y3 <= j <= y5) else None,
            lambda i, j: "-90" if (x2 <= i <= x3) and (y2 <= j <= y4) else None,

            # -45
            lambda i, j: "-45" if (0 <= i <= x1) and (0 <= j <= y1) else None,
            lambda i, j: "-45" if (0 <= i <= x1) and (y2 <= j <= y3) else None,
            lambda i, j: "-45" if (x2 <= i <= x3) and (y4 <= j <= y5) else None,
        ]

        return direction_field, [w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, w11, w12, w13, w14]

    def map2(self):
        w1 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem2900.urdf"),
            [self.x, self.y, self.z],
            self.Orientation000
        )
        w2 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem6500.urdf"),
            [self.x + 2.9 / 2 - self.width / 2, self.y + 6.5 / 2 + self.width / 2, self.z],
            self.Orientation090
        )
        w3 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem2900.urdf"),
            [self.x - self.width, self.y + 6.5, self.z],
            self.Orientation000
        )
        w4 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem6500.urdf"),
            [self.x - 2.9 / 2 - self.width / 2, self.y + 6.5 / 2 - self.width / 2, self.z],
            self.Orientation090
        )
        os.path.join(MODULE_PATH, "data/elem1400-2.urdf")
        #
        w5 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem1400-2.urdf"),
            [self.x + self.width, self.y + 0.7 + self.width / 2 + 0.05, self.z],
            self.Orientation000
        )
        w6 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem5000.urdf"),
            [self.x + self.width - self.width / 2 + 0.65, self.y + 0.7 + self.width + 5.0 / 2, self.z],
            self.Orientation090
        )
        w7 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem1400-2.urdf"),
            [self.x + self.width, self.y + 0.7 + self.width / 2 + 5.0, self.z],
            self.Orientation000
        )

        w8 = self.p.loadURDF(
            os.path.join(MODULE_PATH, "data/elem5000.urdf"),
            [self.x + self.width - self.width / 2 - 0.65, self.y + 0.7 + self.width + 5.0 / 2, self.z],
            self.Orientation090
        )

        x1 = self.x + self.width - self.width / 2 - 0.65
        x2 = self.x + self.width - self.width / 2 + 0.65
        x3 = 2.9 - 0.05 / 2

        y1 = self.y + 0.7 + self.width / 2 + 0.05
        y2 = self.y + 0.7 + self.width / 2 + 5.0
        y3 = -0.05 / 2 + 6.5

        direction_field = [
            # 0
            lambda i, j: "0" if (x1 <= i <= x2) and (0 <= j <= y1) else None,
            lambda i, j: "0" if (0 <= i <= x1) and (0 <= j <= y1) else None,

            # 90
            lambda i, j: "90" if (x2 <= i <= x3) and (y1 <= j <= y2) else None,
            lambda i, j: "90" if (x2 <= i <= x3) and (0 <= j <= y1) else None,

            # 180
            lambda i, j: "180" if (x1 <= i <= x2) and (y2 <= j <= y3) else None,
            lambda i, j: "180" if (x2 <= i <= x3) and (y2 <= j <= y3) else None,

            # -90
            lambda i, j: "-90" if (0 <= i <= x1) and (y1 <= j <= y2) else None,
            lambda i, j: "-90" if (0 <= i <= x1) and (y2 <= j <= y3) else None,
        ]

        return direction_field, [w1, w2, w3, w4, w5, w6, w7, w8]
