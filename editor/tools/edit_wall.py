from core.geometry import Point, Segment
from core.world import World
from .add_wall import AddWall
from ..camera import EditorCamera
from ..renderer import EditorRenderer, WallDrawFlags
from ..input import InputCallable, InputHandler
from enum import IntEnum, auto

import pygame

class EditPoint(IntEnum):
    NoPoint = auto()
    Start = auto()
    End = auto()
    Mid = auto()

class EditWall():
    EditWallColor: tuple[int, int, int] = (221, 176, 31)

    edit_wall: Segment = None
    edit_flags: WallDrawFlags = WallDrawFlags.SurfaceNormal
    edit_point: EditPoint = EditPoint.NoPoint
    editing: bool = False
    remove: bool = False

    @classmethod
    def begin_edit(cls, button: int, down: bool) -> bool:
        # Allow the input to pass through so we may Add Walls
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            return
        
        cls.editing = cls.edit_wall and down
        cls.edit_point = EditPoint.NoPoint if not cls.editing else cls.edit_point
        return cls.editing

    @classmethod
    def remove_wall(cls, button: int, down: bool) -> bool:
        if not down and cls.edit_wall:
            cls.remove = True
            return True
    
    @classmethod
    def flip_wall(cls, button: int, down: bool) -> bool:
        if down and cls.edit_wall is not None:
            # Flip the Edit Point if necessary
            if cls.edit_point == EditPoint.Start:
                cls.edit_point = EditPoint.End
                cls.edit_flags &= ~WallDrawFlags.StartVertex
                cls.edit_flags |= WallDrawFlags.EndVertex
            elif cls.edit_point == EditPoint.End:
                cls.edit_point = EditPoint.Start
                cls.edit_flags &= ~WallDrawFlags.EndVertex
                cls.edit_flags |= WallDrawFlags.StartVertex

            start = cls.edit_wall.start
            cls.edit_wall.start, cls.edit_wall.end = cls.edit_wall.end, start
            return True

    @classmethod
    def update(cls, **kwargs) -> None:
        world: World = kwargs["world"]
        cursor: Point = kwargs["cursor"]
        camera: EditorCamera = kwargs["camera"]
        renderer: EditorRenderer = kwargs["renderer"]

        cursor_world: Point = camera.unproject_point(cursor)

        if AddWall.adding:
            cls.edit_wall = None
        
        if cls.remove and cls.edit_wall:
            world.walls.remove(cls.edit_wall)
            cls.edit_wall = None

        cls.remove = False

        if not cls.editing and not AddWall.adding:
            cursor_scale = (10.0 / camera.zoom, 7.07 / camera.zoom)
            cursor_segments = [
                Segment(cursor_world, Point(-cursor_scale[0],  0.00)            + cursor_world),
                Segment(cursor_world, Point(-cursor_scale[1], -cursor_scale[1]) + cursor_world),
                Segment(cursor_world, Point( 0.00,            -cursor_scale[0]) + cursor_world),
                Segment(cursor_world, Point( cursor_scale[1], -cursor_scale[1]) + cursor_world),
                Segment(cursor_world, Point( cursor_scale[0],  0.00)            + cursor_world),
                Segment(cursor_world, Point( cursor_scale[1],  cursor_scale[1]) + cursor_world),
                Segment(cursor_world, Point( 0.00,             cursor_scale[0]) + cursor_world),
                Segment(cursor_world, Point(-cursor_scale[1],  cursor_scale[1]) + cursor_world),
            ]

            cursor_intersection = min(
                [cursor_segment.intersect_list(world.walls) for cursor_segment in cursor_segments],
                key=lambda result: (result.point - cursor_world).length()
            )

            if not cursor_intersection.hit:
                cls.edit_wall = None
                return
            
            wall: Segment = next(wall for wall in world.walls if wall == cursor_intersection.segment)
            wall_mid: Point = wall.mid()

            closest_vertex = min(
                [vertex for vertex in [wall.start, wall.end, wall_mid]],
                key=lambda vertex: (vertex - cursor_world).length()
            )
            
            cls.edit_wall = wall
            cls.edit_flags: WallDrawFlags = WallDrawFlags.SurfaceNormal
            if closest_vertex == wall.start:
                cls.edit_flags |= WallDrawFlags.StartVertex
                cls.edit_point = EditPoint.Start
            if closest_vertex == wall.end:
                cls.edit_flags |= WallDrawFlags.EndVertex
                cls.edit_point = EditPoint.End
            if closest_vertex == wall_mid:
                cls.edit_flags |= WallDrawFlags.Center
                cls.edit_point = EditPoint.Mid

        if cls.editing:
            cursor_snapped = cls.__snap_point(cursor_world)
            renderer.draw_string(cursor - Point(0.0, 20.0), f"({cursor_snapped.x:.3f}, {cursor_snapped.y:.3f})", (191, 196, 201))

            if cls.edit_point == EditPoint.Start and cls.edit_wall.end != cursor_snapped:
                cls.edit_wall.start = cursor_snapped
            if cls.edit_point == EditPoint.End and cls.edit_wall.start != cursor_snapped:
                cls.edit_wall.end = cursor_snapped
            if cls.edit_point == EditPoint.Mid:
                delta, invdelta = cls.edit_wall.delta(), cls.edit_wall.invdelta()
                cls.edit_wall.start = cls.__snap_point(cursor_world + invdelta * 0.5)
                cls.edit_wall.end = cls.edit_wall.start + delta

        if cls.edit_wall is not None:
            renderer.draw_wall(cls.edit_wall, cls.EditWallColor, cls.edit_flags, 2)
    
    @classmethod
    def __snap_point(cls, point: Point) -> Point:
        return Point(round(point.x * 8.0) / 8.0, round(point.y * 8.0) / 8.0)

InputHandler.add_mouse_button_handler(1, InputCallable(50, EditWall.begin_edit))
InputHandler.add_mouse_button_handler(2, InputCallable(50, EditWall.remove_wall))
InputHandler.add_key_handler(pygame.K_BACKSPACE, InputCallable(50, EditWall.remove_wall))
InputHandler.add_key_handler(pygame.K_DELETE, InputCallable(50, EditWall.remove_wall))
InputHandler.add_key_handler(pygame.K_f, InputCallable(50, EditWall.flip_wall))