from core.geometry import Point, Segment
import math
import pygame
from enum import IntFlag, auto
from typing import Self

from .camera import EditorCamera

class WallDrawFlags(IntFlag):
    SurfaceNormal = auto()
    StartVertex = auto()
    EndVertex = auto()
    Center = auto()

class EditorRenderer():
    DefaultFontName = "helvetica"
    
    def __init__(self: Self, camera: EditorCamera, surface: pygame.Surface) -> None:
        self.__camera = camera
        self.__surface = surface
        self.__font = pygame.font.SysFont(
            self.DefaultFontName if self.DefaultFontName in pygame.font.get_fonts() else pygame.font.get_default_font(),
            14
        )

    def draw_string(self: Self, point: Point, string: str, color: tuple[int, int, int], background: tuple[int, int, int] = None) -> None:
        self.__surface.blit(
            self.__font.render(string, True, color, background),
            (point.x, point.y)
        )

    def draw_line(self: Self, start: Point, end: Point, color: tuple[int, int, int], width: int = 1) -> None:
        pygame.draw.line(
            self.__surface,
            color,
            (start.x, start.y),
            (end.x, end.y),
            width
        )

    def draw_wall(self: Self, wall: Segment, color: tuple[int, int, int], flags: WallDrawFlags = 0, width: int = 1) -> None:
        wall_mid = wall.mid() if flags & (WallDrawFlags.SurfaceNormal | WallDrawFlags.Center) else None
        start, end = self.__camera.project_segment(wall)
        mid = self.__camera.project_point(wall_mid) if wall_mid else None
        pygame.draw.line(
            self.__surface,
            color,
            start,
            end,
            width
        )
        
        if flags & WallDrawFlags.SurfaceNormal:
            surface_normal_end = self.__camera.project_point(wall_mid + wall.surface_normal())
            self.__draw_arrow__(
                (204, 92, 92),
                mid,
                surface_normal_end,
                3
            )
        if flags & WallDrawFlags.StartVertex:
            self.__draw_screen_point__(start, (255, 255, 255), half_size=4)
        if flags & WallDrawFlags.EndVertex:
            self.__draw_screen_point__(end, (255, 255, 255), half_size=4)
        if flags & WallDrawFlags.Center:
            self.__draw_screen_point__(mid, (255, 255, 255), half_size=4)

    def __draw_screen_point__(self: Self, point: tuple[float, float], color: tuple[int, int, int], half_size: int = 1) -> None:
            pygame.draw.rect(
                self.__surface,
                (255, 255, 255),
                (point[0] - half_size, point[1] - half_size,
                 half_size * 2.0, half_size * 2.0)
            )

    def __draw_arrow__(self: Self, color: tuple[int, int, int], start: tuple[float, float], end: tuple[float, float], width: int = 1) -> None:
        leg1 = Point(start[0] - end[0], start[1] - end[1]).normal().rotate(math.pi / 4) * 10.0
        leg2 = Point(start[0] - end[0], start[1] - end[1]).normal().rotate(-math.pi / 4) * 10.0
        pygame.draw.line(
            self.__surface,
            color,
            start,
            end,
            width
        )
        pygame.draw.line(
            pygame.display.get_surface(),
            color,
            end,
            (end[0] + leg1.x, end[1] + leg1.y),
            width
        )
        pygame.draw.line(
            pygame.display.get_surface(),
            color,
            end,
            (end[0] + leg2.x, end[1] + leg2.y),
            width
        )
