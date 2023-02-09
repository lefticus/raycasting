import geometry
import math
import pytest


def test_adding_points():
    p1 = geometry.Point(1, 2)
    p2 = geometry.Point(3, 4)
    result = p1 + p2
    assert result.x == 4
    assert result.y == 6


def test_segment_properties():
    def expected_values(segment, min_x, min_y, max_x, max_y, slope, line, ray):
        assert segment.min_x == min_x
        assert segment.min_y == min_y
        assert segment.max_x == max_x
        assert segment.max_y == max_y

        assert segment.slope == slope
        assert segment.line == line
        assert segment.to_ray() == ray

    zero_slope = geometry.Segment(geometry.Point(0, 0), geometry.Point(1, 0))
    expected_values(
        zero_slope,
        0,
        0,
        1,
        0,
        0,
        geometry.Line(zero_slope.start, 0),
        geometry.Ray(geometry.Point(0, 0), math.pi / 2),
    )

    one_slope = geometry.Segment(geometry.Point(0, 0), geometry.Point(1, 1))
    expected_values(
        one_slope,
        0,
        0,
        1,
        1,
        1,
        geometry.Line(one_slope.start, 1),
        geometry.Ray(geometry.Point(0, 0), math.pi / 4),
    )

    negative_one_slope = geometry.Segment(geometry.Point(0, 0), geometry.Point(1, -1))
    expected_values(
        negative_one_slope,
        0,
        -1,
        1,
        0,
        -1,
        geometry.Line(negative_one_slope.start, -1),
        geometry.Ray(geometry.Point(0, 0), 3 * math.pi / 4),
    )

    vertical_slope = geometry.Segment(geometry.Point(0, 0), geometry.Point(0, 1))
    expected_values(
        vertical_slope,
        0,
        0,
        0,
        1,
        geometry.VERTICAL_SLOPE,
        geometry.Line(vertical_slope.start, geometry.VERTICAL_SLOPE),
        geometry.Ray(geometry.Point(0, 0), 0),
    )


def test_point_segment():
    point_segment = geometry.Segment(geometry.Point(0, 0), geometry.Point(0, 0))
    line_segment = geometry.Segment(geometry.Point(0, 0), geometry.Point(1, 2))

    # make sure these do not throw
    _ = line_segment.line
    _ = line_segment.to_ray()

    # But they should throw if the points are the same
    with pytest.raises(RuntimeError):
        _ = point_segment.line

    with pytest.raises(RuntimeError):
        _ = point_segment.to_ray()


def test_segment_on_segment():

    segment = geometry.Segment(geometry.Point(-23, 10), geometry.Point(15, -32))

    num_points = 40
    d_x = (segment.end.x - segment.start.x) / num_points
    d_y = (segment.end.y - segment.start.y) / num_points

    expected_points = [geometry.Point(segment.start.x + d_x * count, segment.start.y + d_y * count) for count in range(num_points)]

    for point in expected_points:
        assert segment.on_segment(point)

    x_parallel_points = [geometry.Point(point.x + .01, point.y) for point in expected_points]

    for point in x_parallel_points:
        assert not segment.on_segment(point)

    y_parallel_points = [geometry.Point(point.x, point.y + .01) for point in expected_points]

    for point in y_parallel_points:
        assert not segment.on_segment(point)
