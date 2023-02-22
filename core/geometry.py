import functools
import dataclasses
import typing
import math
from numbers import Number
from typing import List

DISTANT_POINT = 100


# Floating point math is hard, and trying to find a point on a line
# can result in some mismatches in floating point values, so we go for "close"
def in_range(min_, max_, value):
    return (min_ - 0.0000001) <= value <= (max_ + 0.0000001)


class Point(typing.NamedTuple):
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        if isinstance(other, Number):
            return Point(self.x * other, self.y * other)
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        raise NotImplemented()
    
    def __div__(self, other):
        if isinstance(other, Point):
            return Point(self.x / other.x, self.y / other.y)
        raise NotImplemented()
    
    def __truediv__(self, other):
        if isinstance(other, Number):
            return Point(self.x / other, self.y / other)
        raise NotImplemented()

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normal(self):
        length = self.length()
        if length == 0.0 or math.isclose(length, 1.0):
            return self
        return Point(self.x / length, self.y / length)
    
    def rotate(self, angle: float):
        cos: float = math.cos(angle)
        sin: float = math.sin(angle)
        return Point(cos, sin) * self.x + Point(-sin, cos) * self.y

@dataclasses.dataclass
class IntersectResult:
    hit: bool = False
    distance: float = 0.0
    segment: 'Segment' = None
    point: Point = Point(0.0, 0.0)

@dataclasses.dataclass(unsafe_hash=True)
class Segment:
    start: Point = Point()
    end: Point = Point()

    def parallel(self, other):
        # Todo - de-duplicate this code
        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.end.x, self.end.y

        x3, y3 = other.start.x, other.start.y
        x4, y4 = other.end.x, other.end.y

        # Calculate the denominator of the t and u values in the parametric equations of the two segments
        return ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)) == 0

    def intersection(self, other):
        if not (
            self.min_x <= other.max_x
            and self.max_x >= other.min_x
            and self.min_y <= other.max_y
            and self.max_y >= other.min_y
        ):
            return None

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
    
    def delta(self):
        return (self.end - self.start)
    
    def invdelta(self):
        return (self.start - self.end)
    
    def mid(self):
        return self.start + self.delta() * 0.5

    def normal(self):
        return self.delta().normal()
    
    def surface_normal(self):
        return self.normal().rotate(math.pi / 2)

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
    
    def intersect_list(self, segments: List['Segment']) -> IntersectResult:
        results: tuple[float, Point, Segment] = intersecting_segments(self, segments)
        results.sort(key=lambda result: result[0])
        
        return IntersectResult() if len(results) == 0 else IntersectResult(
            True,
            results[0][0],
            results[0][2],
            results[0][1]
        )


@dataclasses.dataclass
class Ray:
    start: Point
    angle: float  # Angle from the y-axis, right. "compass coordinates"

    def end_point(self, distance):
        return Point(
            self.start.x + (math.sin(self.angle) * distance),
            self.start.y + (math.cos(self.angle) * distance),
        )

    def to_segment(self, distance=DISTANT_POINT):
        return Segment(self.start, self.end_point(distance))


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
