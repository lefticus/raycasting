import geometry
import pytest


def test_adding_points():
    p1 = geometry.Point(1,2)
    p2 = geometry.Point(3,4)
    result = p1 + p2
    assert result.x == 4
    assert result.y == 6


def test_segment_properties():
    def expected_values(segment, min_x, min_y, max_x, max_y, slope, line):
        assert segment.min_x == min_x
        assert segment.min_y == min_y
        assert segment.max_x == max_x
        assert segment.max_y == max_y

        assert segment.slope == slope
        assert segment.line == line

    zero_slope = geometry.Segment(geometry.Point(0, 0), geometry.Point(1, 0))
    expected_values(zero_slope, 0,0,1,0,0,geometry.Line(zero_slope.start, 0))

    one_slope = geometry.Segment(geometry.Point(0, 0), geometry.Point(1, 1))
    expected_values(one_slope, 0,0,1,1,1,geometry.Line(one_slope.start, 1))

    negative_one_slope = geometry.Segment(geometry.Point(0, 0), geometry.Point(1, -1))
    expected_values(negative_one_slope, 0,-1,1,0,-1,geometry.Line(negative_one_slope.start, -1))

    vertical_slope = geometry.Segment(geometry.Point(0, 0), geometry.Point(0, 1))
    expected_values(vertical_slope, 0,0,0,1,geometry.VERTICAL_SLOPE,geometry.Line(vertical_slope.start, geometry.VERTICAL_SLOPE))

