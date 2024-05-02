"""Cell"""

class Cell:
    """
    Cell - entity that can contain either biological cell 
    or other entity
    """

    def __init__(self, x: int, y: int, entity = None) -> None:
        """Initialize cell"""
        self.x = x
        self.y = y
        self.entity = entity

    @property
    def empty(self) -> bool:
        """Return true if cell is empty"""
        return self.entity is None

    @property
    def entity_id(self) -> int:
        """Return identifier of the entity"""
        return self.entity.ID if self.entity else 0
