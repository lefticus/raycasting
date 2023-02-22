import pygame
import dataclasses
from enum import IntEnum, auto
from typing import Any, Callable, Dict, List

# TODO: ??
class ActionType(IntEnum):
    Down = auto()
    Held = auto()

@dataclasses.dataclass
class InputCallable():
    priority: int
    callback: Callable

class InputHandler():
    __KeyHandlers: Dict[int, List[InputCallable]] = {}
    __MouseButtonHandlers: Dict[int, List[InputCallable]] = {}
    __MouseScrollHandlers: Dict[int, List[InputCallable]] = {}
    __MouseRelativeHandlers: Dict[int, List[InputCallable]] = {}

    @classmethod
    def add_key_handler(cls, key: int, input_callable: InputCallable) -> None:
        cls.__add_handler__(key, input_callable, cls.__KeyHandlers)

    @classmethod
    def add_mouse_button_handler(cls, button: int, input_callable: InputCallable) -> None:
        cls.__add_handler__(button, input_callable, cls.__MouseButtonHandlers)

    @classmethod
    def add_mouse_scroll_handler(cls, input_callable: InputCallable) -> None:
        cls.__add_handler__(0, input_callable, cls.__MouseScrollHandlers)

    @classmethod
    def add_mouse_relative_handler(cls, input_callable: InputCallable) -> None:
        cls.__add_handler__(0, input_callable, cls.__MouseRelativeHandlers)

    @classmethod
    def handle_key(cls, key: int, down: bool):
        cls.__handle_input__(key, cls.__KeyHandlers, key, down)

    @classmethod
    def handle_mouse_button(cls, button: int, down: bool):
        cls.__handle_input__(button, cls.__MouseButtonHandlers, button, down)

    @classmethod
    def handle_mouse_scroll(cls, x: int, y: int):
        cls.__handle_input__(0, cls.__MouseScrollHandlers, x, y)

    @classmethod
    def handle_mouse_relative(cls, x: int, y: int):
        cls.__handle_input__(0, cls.__MouseRelativeHandlers, x, y)

    @classmethod
    def __add_handler__(cls, input: int, input_callable: InputCallable, handler_map: Dict[int, List[InputCallable]]) -> None:
        assert isinstance(input_callable, InputCallable)
        if input not in handler_map:
            handler_map[input] = []
        list = handler_map[input]
        list.append(input_callable)
        list.sort(key=lambda input: input.priority)

    @classmethod
    def __handle_input__(cls, input: int, handler_map: Dict[int, List[InputCallable]], *args: Any, **kwargs: Dict) -> None:
        list = handler_map[input] if input in handler_map else []
        for input_callable in list:
            if input_callable.callback(*args, **kwargs):
                break