import functools
import dataclasses
import typing
import math

VERTICAL_SLOPE = 1e100

# Floating point math is hard, and trying to find a point on a line
# can result in some mismatches in floating point values, so we go for "close"
def in_range(min_, max_, value):
    return (min_ - 0.0000001) <= value <= (max_ + 0.0000001)


class Point(typing.NamedTuple):
    x: float
    y: float

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)


class Line(typing.NamedTuple):
    origin: Point
    slope: float


@dataclasses.dataclass(unsafe_hash=True)
class Segment:
    start: Point
    end: Point

    @functools.cached_property
    def min_x(self):
        return min(self.start.x, self.end.x)

    @functools.cached_property
    def max_x(self):
        return max(self.start.x, self.end.x)

    @functools.cached_property
    def min_y(self):
        return min(self.start.y, self.end.y)

    @functools.cached_property
    def max_y(self):
        return max(self.start.y, self.end.y)

    @functools.cached_property
    def slope(self):
        if self.start.x == self.end.x:
            return VERTICAL_SLOPE
        else:
            return (self.end.y - self.start.y) / (self.end.x - self.start.x)

    @functools.cached_property
    def line(self):
        return Line(self.start, self.slope)

    def on_segment(self, p: Point):
        return in_range(self.min_x, self.max_x, p.x) and in_range(
            self.min_y, self.max_y, p.y
        )

    def ray(self):
        return Ray(
            self.start,
            -math.atan2(self.end.y - self.start.y, self.end.x - self.start.x)
            + math.pi / 2,
        )


@dataclasses.dataclass
class Ray:
    start: Point
    angle: float

    def to_line(self):
        s = math.sin(self.angle)
        if s == 0:
            return Line(self.start, 1e100)
        else:
            return Line(self.start, math.cos(self.angle) / s)

    def distant_point(self):
        return Point(
            self.start.x + (math.sin(self.angle) * 100),
            self.start.y + (math.cos(self.angle) * 100),
        )

    def to_segment(self):
        return Segment(self.start, self.distant_point())


def intercept(l1: Line, l2: Line):
    # x=-(-y2+y1+m2*x2-m1*x1)/(m1-m2)
    # solved from point-slope form
    x = -(
        -l2.origin.y + l1.origin.y + l2.slope * l2.origin.x - l1.slope * l1.origin.x
    ) / (l1.slope - l2.slope)

    # just plug it back into one of the line formulas and get the answer!
    y = l1.slope * (x - l1.origin.x) + l1.origin.y

    return Point(x, y)


def intersect_ray(ray: Ray, segments):
    return intersecting_segments(ray.to_segment(), segments)


def intersecting_segments(input_: Segment, segments):
    input_line = input_.line

    result = []

    for segment in segments:
        if not (
            segment.min_x < input_.max_x
            and segment.max_x > input_.min_x
            and segment.min_y < input_.max_y
            and segment.max_y > input_.min_y
        ):
            continue

        segment_line = segment.line

        # if not parallel
        if input_line.slope != segment_line.slope:
            p = intercept(input_line, segment_line)

            if segment.on_segment(p) and input_.on_segment(p):
                result.append((math.dist(input_.start, p), p, segment))

    return result
