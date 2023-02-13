import geometry
import math
import pytest

import raycasting


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

    expected_points = [
        geometry.Point(segment.start.x + d_x * count, segment.start.y + d_y * count)
        for count in range(num_points)
    ]

    for point in expected_points:
        assert segment.on_segment(point)

    x_parallel_points = [
        geometry.Point(point.x + 0.01, point.y) for point in expected_points
    ]

    for point in x_parallel_points:
        assert not segment.on_segment(point)

    y_parallel_points = [
        geometry.Point(point.x, point.y + 0.01) for point in expected_points
    ]

    for point in y_parallel_points:
        assert not segment.on_segment(point)


def test_ray_properties():
    def expected_values(ray, line, segment):
        actual_line = ray.to_line()
        assert actual_line.slope == pytest.approx(line.slope)
        assert actual_line.origin == line.origin

        actual_segment = ray.to_segment()
        assert actual_segment.start.x == pytest.approx(segment.start.x)
        assert actual_segment.start.y == pytest.approx(segment.start.y)
        assert actual_segment.end.x == pytest.approx(segment.end.x)
        assert actual_segment.end.y == pytest.approx(segment.end.y)

    zero_angle = geometry.Ray(geometry.Point(0, 0), 0)
    expected_values(
        zero_angle,
        geometry.Line(geometry.Point(0, 0), geometry.VERTICAL_SLOPE),
        geometry.Segment(
            geometry.Point(0, 0), geometry.Point(0, geometry.DISTANT_POINT)
        ),
    )

    forty_five_angle = geometry.Ray(geometry.Point(0, 0), math.pi / 4)
    expected_values(
        forty_five_angle,
        geometry.Line(geometry.Point(0, 0), 1),
        geometry.Segment(
            geometry.Point(0, 0),
            geometry.Point(
                math.sin(math.pi / 4) * geometry.DISTANT_POINT,
                math.cos(math.pi / 4) * geometry.DISTANT_POINT,
            ),
        ),
    )

    right_angle = geometry.Ray(geometry.Point(0, 0), math.pi / 2)
    expected_values(
        right_angle,
        geometry.Line(geometry.Point(0, 0), 0),
        geometry.Segment(
            geometry.Point(0, 0), geometry.Point(geometry.DISTANT_POINT, 0)
        ),
    )

    one_eighty_angle = geometry.Ray(geometry.Point(0, 0), math.pi)
    expected_values(
        one_eighty_angle,
        geometry.Line(geometry.Point(0, 0), -geometry.VERTICAL_SLOPE),
        geometry.Segment(
            geometry.Point(0, 0), geometry.Point(0, -geometry.DISTANT_POINT)
        ),
    )


def test_ray_segment_round_trip():
    def round_trip(ray: geometry.Ray):
        segment = ray.to_segment()
        new_ray = segment.to_ray()

        assert (ray.angle % (2 * math.pi)) == pytest.approx(new_ray.angle)
        assert ray.start == new_ray.start

    angle_0 = geometry.Ray(geometry.Point(0, 0), 0)
    angle_45 = geometry.Ray(geometry.Point(0, 0), math.pi / 4)
    angle_90 = geometry.Ray(geometry.Point(0, 0), math.pi / 2)
    angle_180 = geometry.Ray(geometry.Point(0, 0), math.pi)
    angle_270 = geometry.Ray(geometry.Point(0, 0), 3 * math.pi / 2)
    angle_405 = geometry.Ray(geometry.Point(0, 0), 2 * math.pi + math.pi / 4)

    round_trip(angle_0)
    round_trip(angle_45)
    round_trip(angle_90)
    round_trip(angle_180)
    round_trip(angle_270)
    round_trip(angle_405)


def test_line_intersections():
    horizontal = geometry.Line(geometry.Point(0,0), 0)
    vertical = geometry.Line(geometry.Point(5, 5), -geometry.VERTICAL_SLOPE)

    intersection1 = geometry.intercept(horizontal, vertical)
    assert intersection1.x == pytest.approx(5)
    assert intersection1.y == pytest.approx(0)

    intersection2 = geometry.intercept(vertical, horizontal)
    assert intersection2.x == pytest.approx(5)
    assert intersection2.y == pytest.approx(0)


def test_segment_intersections():
    horizontal = geometry.Segment(geometry.Point(-1, 0), geometry.Point(1, 0))
    vertical = geometry.Segment(geometry.Point(0, -1), geometry.Point(0, 1))

    intersections = geometry.intersecting_segments(horizontal, [vertical])
    
    assert len(intersections) == 1
    assert intersections[0][2] == vertical
    assert intersections[0][1].x == pytest.approx(0)
    assert intersections[0][1].y == pytest.approx(0)

    intersections = geometry.intersecting_segments(vertical, [horizontal])

    assert len(intersections) == 1
    assert intersections[0][2] == horizontal
    assert intersections[0][1].x == pytest.approx(0)
    assert intersections[0][1].y == pytest.approx(0)


def test_intersect_ray_to_perpendicular():
    ray = geometry.Ray(geometry.Point(10, 5), math.pi)
    segment = geometry.Segment(geometry.Point(0, 0), geometry.Point(20, 0))
    intersections = geometry.intersect_ray(ray, [segment])
    assert len(intersections) == 1


def test_intersect_ray_to_diagonal():
    ray = geometry.Ray(geometry.Point(10, 5), math.pi)
    segment = geometry.Segment(geometry.Point(0, 0), geometry.Point(20, -20))
    intersections = geometry.intersect_ray(ray, [segment])
    assert len(intersections) == 1


def test_camera_ray_intersections():
    camera = raycasting.Camera(geometry.Point(10, 5), math.pi, math.pi / 4)
    segment = geometry.Segment(geometry.Point(0, 0), geometry.Point(20, 0))
    segment2 = geometry.Segment(geometry.Point(0, 0), geometry.Point(40, -40))

    for ray, point in camera.rays(10):
        intersections = geometry.intersect_ray(ray, [segment, segment2])
        assert len(intersections) == 2
