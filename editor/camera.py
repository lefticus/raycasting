from core.geometry import Point, Segment
import pygame
from enum import IntFlag, auto
#from geometry import *
from typing import Self

from .input import InputCallable, InputHandler

class MoveMode(IntFlag):
    Keyboard = auto()
    Mouse = auto()

class EditorCamera():
    def __init__(self: Self, width: int, height: int, zoom_clamp: tuple[float, float]=(8.0, 400.0)):
        self.__zoom_clamp: tuple[float, float] = zoom_clamp
        self.__zoom: float = self.__zoom_clamp[0]
        self.__move_speed: float = 2.0
        self.__move_mode: MoveMode = MoveMode.Keyboard
        self.__location: Point = Point(0.0, 0.0)
        self.__move: Point = Point(0.0, 0.0)

        self.set_dimensions(width, height)

        InputHandler.add_mouse_button_handler(3, InputCallable(100.0, self.toggle_move_mode))
        InputHandler.add_mouse_scroll_handler(InputCallable(100.0, self.mouse_scroll))
        InputHandler.add_mouse_relative_handler(InputCallable(100.0, self.mouse_relative))
        InputHandler.add_key_handler(pygame.K_UP,  InputCallable(100.0, self.move_up))
        InputHandler.add_key_handler(pygame.K_DOWN, InputCallable(100.0, self.move_down))
        InputHandler.add_key_handler(pygame.K_LEFT, InputCallable(100.0, self.move_left))
        InputHandler.add_key_handler(pygame.K_RIGHT, InputCallable(100.0, self.move_right))
    
    @property
    def center(self: Self) -> Point:
        return self.__center
    
    @property
    def location(self: Self) -> Point:
        return self.__location
    
    @property
    def zoom(self: Self) -> float:
        return self.__zoom
    
    """
    Input Handlers
    """
    def mouse_scroll(self: Self, x: int, y: int) -> bool:
        self.__zoom = min(self.__zoom_clamp[1], max(self.__zoom_clamp[0], self.__zoom + y * 2.0))
        return True
    
    def mouse_relative(self: Self, x: int, y: int) -> bool:
        if not (self.__move_mode & MoveMode.Mouse):
            return False

        self.__move = Point(-x / self.__zoom, y / self.__zoom)
        return True
    
    def toggle_move_mode(self: Self, button: int, down: bool) -> bool:
        if down:
            self.__move_mode |= MoveMode.Mouse
        else:
            self.__move_mode &= ~MoveMode.Mouse
        return True
    
    def move_up(self: Self, key: int, down: bool) -> bool:
        return self.__add_move__(Point(0.0, 1.0 if down else -1.0))
    
    def move_down(self: Self, key: int, down: bool) -> bool:
        return self.__add_move__(Point(0.0, -1.0 if down else 1.0))
    
    def move_left(self: Self, key: int, down: bool) -> bool:
        return self.__add_move__(Point(-1.0 if down else 1.0, 0.0))
    
    def move_right(self: Self, key:int, down: bool) -> bool:
        return self.__add_move__(Point(1.0 if down else -1.0, 0.0))
    
    def __add_move__(self: Self, movement: Point) -> bool:
        if self.__move_mode & MoveMode.Mouse:
            return False
        
        self.__move = Point(
            min(1.0, max(-1.0, self.__move.x + movement.x)),
            min(1.0, max(-1.0, self.__move.y + movement.y))
        )
        return True
    
    """
    Functionality
    """
    def set_dimensions(self: Self, width: int, height: int) -> None:
        self.__center = Point(width * 0.5, height * 0.5)

    def tick(self: Self, elapsed: float) -> None:
        zoom_accel = self.__zoom_clamp[1] / self.__zoom

        self.__location += self.__move if self.__move_mode & MoveMode.Mouse else self.__move * self.__move_speed * zoom_accel * elapsed
        if self.__move_mode & MoveMode.Mouse:
            self.__move = Point(0.0, 0.0)

    def project_point(self: Self, point: Point) -> tuple[float, float]:
        projected = Point(point.x - self.location.x, self.location.y - point.y) * self.__zoom + self.__center
        return (projected.x, projected.y)

    def project_segment(self: Self, segment: Segment) -> Segment:
        return self.project_point(segment.start), self.project_point(segment.end)

    def unproject_point(self: Self, point: Point) -> Point:
        return Point(point.x - self.__center.x, self.__center.y - point.y) / self.__zoom + self.location