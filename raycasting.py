import math
import pygame
import time
import functools
import dataclasses
import typing


class Point(typing.NamedTuple):
    x: float
    y: float

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)


# Floating point math is hard, and trying to find a point on a line
# can result in some mismatches in floating point values, so we go for "close"
def in_range(min_, max_, value):
    return (min_ - 0.0000001) <= value <= (max_ + 0.0000001)


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
            return 1e100
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


class Camera:
    def __init__(self, location: Point, direction, viewing_angle):
        self.location = location
        self.direction = direction
        self.viewing_angle = viewing_angle

    def try_move(self, distance, walls):
        new_location = self.location + Point(
            distance * -math.sin(self.direction), distance * -math.cos(self.direction)
        )

        proposed_move = Segment(self.location, new_location)

        if len(intersecting_segments(proposed_move, walls)) == 0:
            # we don't intersect any wall, so we allow the move
            self.location = new_location

    def rotate(self, angle):
        self.direction += angle

    def rays(self, count):
        # The idea is that we are creating a line
        # through which to draw the rays, so we get a more correct
        # (not curved) distribution of rays, but we still need
        # to do a height correction later to flatten it out
        start_angle = self.direction - self.viewing_angle / 2
        end_angle = start_angle + self.viewing_angle

        viewing_plane_start = self.location + Point(
            math.sin(start_angle), math.cos(start_angle)
        )
        viewing_plane_end = self.location + Point(
            math.sin(end_angle), math.cos(end_angle)
        )

        d_x = (viewing_plane_end.x - viewing_plane_start.x) / count
        d_y = (viewing_plane_end.y - viewing_plane_start.y) / count

        location = self.location

        for current in range(count):
            plane_point = Point(
                viewing_plane_start.x + (d_x * current),
                viewing_plane_start.y + (d_y * current),
            )
            ray_segment = Segment(location, plane_point)

            yield ray_segment.ray(), plane_point


def box(ul: Point):
    return [
        Segment(ul + Point(0, 0), ul + Point(1, 0)),
        Segment(ul + Point(1, 0), ul + Point(1, -1)),
        Segment(ul + Point(0, 0), ul + Point(0, -1)),
        Segment(ul + Point(0, -1), ul + Point(1, -1)),
    ]


def lr_triangle(ul: Point):
    return [
        Segment(ul + Point(0, -1), ul + Point(1, -1)),
        Segment(ul + Point(1, 0), ul + Point(1, -1)),
        Segment(ul + Point(0, -1), ul + Point(1, 0)),
    ]


def ur_triangle(ul: Point):
    return [
        Segment(ul + Point(0, 0), ul + Point(1, 0)),
        Segment(ul + Point(1, 0), ul + Point(1, -1)),
        Segment(ul + Point(0, 0), ul + Point(1, -1)),
    ]


def ll_triangle(ul: Point):
    return [
        Segment(ul + Point(0, 0), ul + Point(1, -1)),
        Segment(ul + Point(0, -1), ul + Point(1, -1)),
        Segment(ul + Point(0, 0), ul + Point(0, -1)),
    ]


def ul_triangle(ul: Point):
    return [
        Segment(ul + Point(0, 0), ul + Point(1, 0)),
        Segment(ul + Point(1, 0), ul + Point(0, -1)),
        Segment(ul + Point(0, 0), ul + Point(0, -1)),
    ]


def make_map(map_string):
    result = []
    lines = map_string.split("\n")

    # start from top of map and work down
    y = len(lines)

    for line in lines:
        x = 0
        for char in line:
            if char == "#" or char == "*":
                result += box(Point(x, y))
            if char == "/":
                result += ul_triangle(Point(x, y))
            if char == "&":
                result += ur_triangle(Point(x, y))
            if char == "%":
                result += lr_triangle(Point(x, y))
            if char == "`":
                result += ll_triangle(Point(x, y))

            x += 1
        y -= 1

    print(f"Segments: {len(result)}")

    # if any segment exists twice, then it was between two map items
    # and both can be removed!
    result = [item for item in result if result.count(item) == 1]

    print(f"Filtered duplicated wall segments: {len(result)}")

    cont = True
    while cont:
        remove_list = []
        for s in result:
            for n in result:
                if s.end.x == n.start.x and s.end.y == n.start.y and n.slope == s.slope:
                    remove_list += [n, s]
                    result.append(
                        Segment(Point(s.start.x, s.start.y), Point(n.end.x, n.end.y))
                    )
                    break
                elif (
                    s is not n
                    and s.end.x == n.end.x
                    and s.end.y == n.end.y
                    and n.slope == s.slope
                ):
                    remove_list += [n, s]
                    result.append(
                        Segment(
                            Point(s.start.x, s.start.y), Point(n.start.x, n.start.y)
                        )
                    )
                    break
                elif (
                    s is not n
                    and s.start.x == n.start.x
                    and s.start.y == n.start.y
                    and n.slope == s.slope
                ):
                    remove_list += [n, s]
                    result.append(
                        Segment(Point(s.end.x, s.end.y), Point(n.end.x, n.end.y))
                    )
                    break

            if len(remove_list) > 0:
                break

        if len(remove_list) == 0:
            cont = False

        for i in remove_list:
            result.remove(i)

    print(f"Merged segments: {len(result)}")

    return result


#
# Symbols:
#
#  /  ###   # or *  ### & ###  %    #  `  #
#     ##            ###    ##      ##     ##
#     #             ###     #     ###     ###
#


game_map = """
###########`&#######
#           ` / /  #
#/%#/&`&/&`& % `%`&#
# / %  / `/% &  /  #
#& / `   & / & /%/%#
# `&  & `& ` `% ` &#
#  % # / `%&  # `& #
#% /% %`` / %/& &  #
#/% /   &`%/ % /%& #
# # //&    %& %`&  #
#  % %`  %/     % &#
####################
"""

map_wall_segments = make_map(game_map)

pygame.init()

width = 800
height = 480

screen = pygame.display.set_mode((width, height))

c = Camera(Point(-0.5, -0.5), math.pi / 2, (width / height))

frame = 0
last_time = time.perf_counter()

while True:
    pygame.display.get_surface().fill((0, 0, 0))

    frame += 1

    if frame % 10 == 0:
        new_time = time.perf_counter()
        elapsed, last_time = new_time - last_time, new_time

        print(f"{10 / elapsed} fps ({c.location.x},{c.location.y})")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        c.try_move(-0.08, map_wall_segments)
    if keys[pygame.K_DOWN]:
        c.try_move(0.08, map_wall_segments)
    if keys[pygame.K_RIGHT]:
        c.rotate(math.pi / 60)
    if keys[pygame.K_LEFT]:
        c.rotate(-math.pi / 60)

    col = 0

    last_match = None
    last_wall = None

    for r, segment_point in c.rays(width):
        matches = intersect_ray(r, map_wall_segments)

        def sort_criteria(line):
            return line[0]

        # sort by closest, and draw it
        matches.sort(key=sort_criteria, reverse=False)

        # only draw the closest wall.
        if len(matches) > 0 and matches[0][0] != 0:
            distance_from_eye = matches[0][0]

            # Distance correction from https://gamedev.stackexchange.com/questions/45295/raycasting-fisheye-effect-question
            corrected_distance = distance_from_eye * math.cos(c.direction - r.angle)

            wall_height = (height * 0.75) / corrected_distance
            if wall_height > height:
                wall_height = height + 2

            wall_start = (height - wall_height) / 2
            wall_end = wall_start + wall_height

            # Draw edge if detected
            if last_match is not matches[0][2] and col != 0:
                if last_match is None:
                    pygame.draw.line(
                        pygame.display.get_surface(),
                        (255, 255, 255),
                        (col, wall_start),
                        (col, wall_end),
                    )
                else:
                    pygame.draw.line(
                        pygame.display.get_surface(),
                        (255, 255, 255),
                        (col, min(wall_start, last_wall[0])),
                        (col, max(wall_end, last_wall[1])),
                    )
            else:
                # draw just top and bottom points otherwise
                screen.set_at((col, int(wall_start)), (255, 255, 255))
                screen.set_at((col, int(wall_end)), (255, 255, 255))

                # and some texture...
                texture_size = int(height / 50)
                if col % texture_size == 0:
                    for y in range(int(wall_start), int(wall_end), texture_size):
                        screen.set_at((col, y), (255, 255, 255))

            last_wall = (wall_start, wall_end)
            last_match = matches[0][2]
        else:
            # Look for transition from wall to empty space, draw edge
            if last_match is not None:
                pygame.draw.line(
                    pygame.display.get_surface(),
                    (255, 255, 255),
                    (col, last_wall[0]),
                    (col, last_wall[1]),
                )
            last_match = None

        col += 1

    pygame.display.flip()
