import functools
import dataclasses
import typing
import math

DISTANT_POINT = 100


# Floating point math is hard, and trying to find a point on a line
# can result in some mismatches in floating point values, so we go for "close"
def in_range(min_, max_, value):
    return (min_ - 0.0000001) <= value <= (max_ + 0.0000001)


class Point(typing.NamedTuple):
    x: float
    y: float

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)


@dataclasses.dataclass(unsafe_hash=True)
class Segment:
    start: Point
    end: Point

    def parallel(self, other):
        # Todo - de-duplicate this code
        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.end.x, self.end.y

        x3, y3 = other.start.x, other.start.y
        x4, y4 = other.end.x, other.end.y

        # Calculate the denominator of the t and u values in the parametric equations of the two segments
        return ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)) == 0

    def intersection(self, other):
        # This version is cribbed from ChatGPT, and it passes our tests for
        # line intersection calculations

        # Calculate the differences between the start and end points of the two segments

        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.end.x, self.end.y

        x3, y3 = other.start.x, other.start.y
        x4, y4 = other.end.x, other.end.y

        # Calculate the denominator of the t and u values in the parametric equations of the two segments
        denominator = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

        # Check if the two segments are parallel (i.e., their parametric equations don't intersect)
        if denominator == 0:
            return None

        # Calculate the t and u values in the parametric equations of the two segments
        t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / denominator
        u = ((x1 - x2) * (y3 - y1) - (y1 - y2) * (x3 - x1)) / denominator

        # Check if the two segments intersect
        if 0 <= t <= 1 and 0 <= u <= 1:
            # Calculate the point of intersection
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return Point(x, y)
        else:
            return None

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

    def in_bounds(self, p: Point):
        return in_range(self.min_x, self.max_x, p.x) and in_range(
            self.min_y, self.max_y, p.y
        )

    def to_ray(self):
        if self.start == self.end:
            # no possible valid Ray object
            raise RuntimeError("Cannot create Ray from identical segment points")

        # Correct from angle above x axis as returned by atan2, to angle
        # away from y axis, as is in our coordinate system
        return Ray(
            self.start,
            -math.atan2(self.end.y - self.start.y, self.end.x - self.start.x)
            + math.pi / 2,
        )


@dataclasses.dataclass
class Ray:
    start: Point
    angle: float

    def distant_point(self):
        return Point(
            self.start.x + (math.sin(self.angle) * DISTANT_POINT),
            self.start.y + (math.cos(self.angle) * DISTANT_POINT),
        )

    def to_segment(self):
        return Segment(self.start, self.distant_point())


def intersect_ray(ray: Ray, segments):
    return intersecting_segments(ray.to_segment(), segments)


def intersecting_segments(input_: Segment, segments):
    result = []

    for segment in segments:
        intersection = input_.intersection(segment)

        if intersection is not None:
            result.append(
                (math.dist(input_.start, intersection), intersection, segment)
            )

    return result
