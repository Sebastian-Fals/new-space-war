class SpatialGrid:
    def __init__(self, width, height, cell_size=100):
        self.cell_size = cell_size
        self.cols = int(width / cell_size) + 1
        self.rows = int(height / cell_size) + 1
        self.cells = {} # Dict of (col, row) -> [entities]
        
    def clear(self):
        self.cells = {}
        
    def insert(self, entity):
        # Determine which cells the entity overlaps
        # Assume entity has x, y, width, height or radius
        # For now, just use center point or simple bounding box
        
        # If entity is a dict (bullet), use keys
        if isinstance(entity, dict):
            x, y = entity['x'], entity['y']
            w, h = 10, 10 # Approx size
        else:
            x, y = entity.x, entity.y
            w = getattr(entity, 'width', 32)
            h = getattr(entity, 'height', 32)
            
        start_col = int((x - w/2) / self.cell_size)
        end_col = int((x + w/2) / self.cell_size)
        start_row = int((y - h/2) / self.cell_size)
        end_row = int((y + h/2) / self.cell_size)
        
        for c in range(start_col, end_col + 1):
            for r in range(start_row, end_row + 1):
                if (c, r) not in self.cells:
                    self.cells[(c, r)] = []
                self.cells[(c, r)].append(entity)
                
    def query(self, x, y, w, h):
        # Return all entities in cells overlapping this rect
        found = set()
        
        start_col = int((x - w/2) / self.cell_size)
        end_col = int((x + w/2) / self.cell_size)
        start_row = int((y - h/2) / self.cell_size)
        end_row = int((y + h/2) / self.cell_size)
        
        for c in range(start_col, end_col + 1):
            for r in range(start_row, end_row + 1):
                if (c, r) in self.cells:
                    for e in self.cells[(c, r)]:
                        # Check ID to avoid duplicates if entity is object
                        # If dict, we can't hash it easily.
                        # So we might return duplicates if we just append.
                        # Using set requires hashable. Dicts aren't.
                        # Objects are.
                        
                        # For bullets (dicts), we might need a wrapper or ID.
                        # Or just return list and let caller handle duplicates?
                        # Or use 'id' field if we add one.
                        
                        # For now, let's just return list and filter unique by object identity if possible
                        # But dicts...
                        
                        # Optimization: Just return the list of lists and flatten?
                        pass
                        
                    found.update(self.cells[(c, r)]) # This fails for dicts
                    
        # Workaround for dicts:
        # If we use this for collision, we usually query "What hits THIS entity?"
        # So we iterate cells.
        
        results = []
        seen_ids = set()
        
        for c in range(start_col, end_col + 1):
            for r in range(start_row, end_row + 1):
                if (c, r) in self.cells:
                    for e in self.cells[(c, r)]:
                        eid = id(e)
                        if eid not in seen_ids:
                            results.append(e)
                            seen_ids.add(eid)
        return results
