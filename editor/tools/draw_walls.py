from core.world import World
from ..renderer import EditorRenderer

class DrawWalls():
    WallColor: tuple[int, int, int] = (191, 196, 201)

    @classmethod
    def update(cls, **kwargs) -> None:
        world: World = kwargs["world"]
        renderer: EditorRenderer = kwargs["renderer"]

        for wall in world.walls:
            renderer.draw_wall(wall, cls.WallColor)