"""Cell"""


class Cell:
    """
    Cell - entity that can contain either biological cell
    or other entity
    """

    __dict__ = [
        "x",
        "y",
        "_entity",
        "neighbors",
        "add_entity_callback",
        "remove_entity_callback",
    ]

    def __init__(self, x: int, y: int, entity=None) -> None:
        """Initialize cell"""
        self.x = x
        self.y = y
        self._entity = entity
        self.neighbors = []
        self.distance = 0
        self.phi = 0

        self.add_entity_callback = None
        self.remove_entity_callback = None

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    @property
    def entity(self):
        """Return entity"""
        return self._entity

    @entity.setter
    def entity(self, entity_) -> None:
        if self.empty and entity_ is not None:
            self.add_entity_callback(self)

        if entity_ is None and not self.empty:
            self.remove_entity_callback(self)

        self._entity = entity_

    @property
    def empty(self) -> bool:
        """Return true if cell is empty"""
        return self.entity is None

    @property
    def entity_id(self) -> int:
        """Return identifier of the entity"""
        return self.entity.ID if self.entity else 0

    @property
    def color(self):
        if self.entity:
            return self.entity.color
        return 0, 0, 0

    def get_free_neighbor(self):
        """Return empty cell"""
        return [cell for cell in self.neighbors if cell.empty]
