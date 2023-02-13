import pygame
import time
from geometry import *


class Camera:
    def __init__(self, location: Point, direction, viewing_angle):
        self.location = location
        self.direction = direction
        self.viewing_angle = viewing_angle
        self.planar_projection = True

    def try_move(self, distance, walls):
        new_location = self.location + Point(
            distance * math.sin(self.direction), distance * math.cos(self.direction)
        )

        proposed_move = Segment(self.location, new_location)

        if len(intersecting_segments(proposed_move, walls)) == 0:
            # we don't intersect any wall, so we allow the move
            self.location = new_location

    def rotate(self, angle):
        self.direction = (self.direction + angle) % (2 * math.pi)

    def rays(self, count):
        # The idea is that we are creating a line
        # through which to draw the rays, so we get a more correct
        # (not curved) distribution of rays, but we still need
        # to do a height correction later to flatten it out

        start_angle = self.direction - self.viewing_angle / 2
        end_angle = start_angle + self.viewing_angle

        if self.planar_projection:
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

                yield ray_segment.to_ray(), plane_point
        else:
            angle_slice = self.viewing_angle / count

            for current in range(count):
                yield Ray(
                    self.location, start_angle + current * angle_slice
                ), self.location


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

def main():

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

    FOV = 2 * math.atan((width / 800) * math.tan((math.pi / 2) / 2))

    c = Camera(Point(-0.5, -0.5), math.pi / 2, FOV)

    frame = 0
    last_time = time.perf_counter()

    fisheye_distance_correction = True

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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    c.planar_projection = not c.planar_projection
                if event.key == pygame.K_2:
                    fisheye_distance_correction = not fisheye_distance_correction

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            c.try_move(0.08, map_wall_segments)
        if keys[pygame.K_DOWN]:
            c.try_move(-0.08, map_wall_segments)
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
                corrected_distance = (
                    distance_from_eye * math.cos(c.direction - r.angle)
                    if fisheye_distance_correction
                    else distance_from_eye
                )

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


if __name__ == "__main__":
    main()
