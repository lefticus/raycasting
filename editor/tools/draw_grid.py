from core.geometry import Point
from ..camera import EditorCamera
from ..renderer import EditorRenderer

class DrawGrid():
    GridColor: tuple[int, int, int] = (41, 46, 51)
    HalfGridColor: tuple[int, int, int] = (29, 34, 39)

    @classmethod
    def update(cls, **kwargs) -> None:
        camera: EditorCamera = kwargs["camera"]
        renderer: EditorRenderer = kwargs["renderer"]

        grid_size = camera.zoom
        grid_count = (int(camera.center.x / grid_size) + 2, int(camera.center.y / grid_size) + 2)
        center = camera.project_point(Point(int(camera.location.x), int(camera.location.y)))
        vertical_offset = Point(center[0], 0.0)
        horizontal_offset = Point(0.0, center[1])
        width = Point(camera.center.x * 2.0, 0.0)
        height = Point(0.0, camera.center.y * 2.0)

        def draw(multiplier: int, color: tuple[int, int, int]) -> None:
            for current in range(-grid_count[0] * multiplier, grid_count[0] * multiplier):
                grid_current = grid_size / multiplier * current
                vertical = vertical_offset + Point(grid_current, 0.0)
                renderer.draw_line(vertical, vertical + height, color)

            for current in range(-grid_count[1] * multiplier, grid_count[1] * multiplier):
                grid_current = grid_size / multiplier * current
                horizontal = horizontal_offset + Point(0.0, grid_current)
                renderer.draw_line(horizontal, horizontal + width, color)
        
        if grid_size > 256.0:
            draw(8, cls.HalfGridColor)

        if grid_size > 128.0:
            draw(4, cls.HalfGridColor)

        if grid_size > 64.0:
            draw(2, cls.HalfGridColor)

        draw(1, cls.GridColor)