"""Cell"""

class Cell:
    """
    Cell - entity that can contain either biological cell 
    or other entity
    """

    def __init__(self, x: int, y: int,
                 entity = None) -> None:
        """Initialize cell"""
        self.x = x
        self.y = y
        self._entity = entity
        self.neighbors = []

        self.add_entity_callback = None
        self.remove_entity_callback = None

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
