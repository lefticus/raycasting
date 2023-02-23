from core.geometry import Point, Segment
from core.world import World
from ..camera import EditorCamera
from ..renderer import EditorRenderer, WallDrawFlags
from ..input import InputCallable, InputHandler

import pygame

class AddWall():
    AddWallColor: tuple[int, int, int] = (92, 178, 204)

    add_wall: Segment = None
    flipped: bool = False
    adding: bool = False

    @classmethod
    def begin_add(cls, button: int, down: bool) -> bool:
        cls.adding = down
        return True
    
    @classmethod
    def flip_wall(cls, button: int, down: bool) -> bool:
        if down and cls.add_wall is not None:
            cls.flipped = not cls.flipped

            start = cls.add_wall.start
            cls.add_wall.start, cls.add_wall.end = cls.add_wall.end, start
            return True

    @classmethod
    def update(cls, **kwargs) -> None:
        world: World = kwargs["world"]
        cursor: Point = kwargs["cursor"]
        camera: EditorCamera = kwargs["camera"]
        renderer: EditorRenderer = kwargs["renderer"]

        cursor_world: Point = camera.unproject_point(cursor)

        if not cls.adding:
            #TODO: Add a filter to see if this wall is in world.walls OR if it falls inside an existing wall.
            #      The former is achievable by simply doing `if cls.add_wall not in world.walls` but both
            #      checks should likely be performed together over the entire wall.
            if cls.add_wall is not None and cls.add_wall.start != cls.add_wall.end:
                world.walls.append(cls.add_wall)
            
            cls.add_wall = None
            return

        cursor_snapped = cls.__snap_point(cursor_world)
        if cls.add_wall is None:
            cls.add_wall = Segment(cursor_snapped, cursor_snapped)
            cls.flipped = False

        if cls.flipped:
            cls.add_wall.start = cursor_snapped
        else:
            cls.add_wall.end = cursor_snapped
        renderer.draw_wall(cls.add_wall, cls.AddWallColor, WallDrawFlags.StartVertex | WallDrawFlags.EndVertex | WallDrawFlags.SurfaceNormal, 2)
        renderer.draw_string(cursor - Point(0.0, 20.0), f"({cursor_snapped.x:.3f}, {cursor_snapped.y:.3f})", (191, 196, 201), (21, 26, 31))
    
    @classmethod
    def __snap_point(cls, point: Point) -> Point:
        return Point(round(point.x * 8.0) / 8.0, round(point.y * 8.0) / 8.0)

InputHandler.add_mouse_button_handler(1, InputCallable(75, AddWall.begin_add))
InputHandler.add_key_handler(pygame.K_f, InputCallable(75, AddWall.flip_wall))