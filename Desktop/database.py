import os
import sys

# Custom Node for our In-Memory Index (Replacing built-in dict/map)
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class KeyValueStore:
    def __init__(self, filename="data.db"):
        self.filename = filename
        self.head = None  # Head of our linked list index
        self._load_from_disk()

    def _update_index(self, key, value):
        """Updates the in-memory linked list. Enforces 'last write wins'."""
        current = self.head
        while current:
            if current.key == key:
                current.value = value
                return
            current = current.next
        
        # Key not found, prepend new node to the list
        new_node = Node(key, value)
        new_node.next = self.head
        self.head = new_node

    def _load_from_disk(self):
        """Replays the append-only log to rebuild the index on startup."""
        if not os.path.exists(self.filename):
            return
        
        with open(self.filename, "r") as f:
            for line in f:
                # Expecting format: SET <key> <value>
                parts = line.strip().split(" ", 2)
                if len(parts) == 3 and parts[0] == "SET":
                    self._update_index(parts[1], parts[2])

    def set(self, key, value):
        """Persists to append-only log and updates index."""
        with open(self.filename, "a") as f:
            f.write(f"SET {key} {value}\n")
        self._update_index(key, value)

    def get(self, key):
        """Retrieves value from the in-memory index."""
        current = self.head
        while current:
            if current.key == key:
                return current.value
            current = current.next
        return None

def main():
    db = KeyValueStore()

    # Process commands from STDIN
    for line in sys.stdin:
        parts = line.strip().split()
        if not parts:
            continue

        command = parts[0].upper()

        if command == "SET" and len(parts) >= 3:
            key = parts[1]
            value = " ".join(parts[2:]) # Handles values with spaces
            db.set(key, value)

        elif command == "GET" and len(parts) == 2:
            key = parts[1]
            result = db.get(key)
            if result is not None:
                print(result)
            else:
                print("") # Requirement: output nothing/blank for missing keys

        elif command == "EXIT":
            break

if __name__ == "__main__":
    main()
