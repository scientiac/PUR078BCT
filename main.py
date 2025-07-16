import random
from typing import List, Tuple, Dict, Set

class NameCrossword:
    def __init__(self, width: int = 50, height: int = 30):
        self.width = width
        self.height = height
        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        self.placed_words = []
        self.word_positions = {}  # Track word positions to avoid unwanted connections
        
    def extract_first_names(self, full_names: List[str]) -> List[str]:
        """Extract first names from the full names list"""
        first_names = []
        for name in full_names:
            if name.strip():  # Skip empty names
                parts = name.strip().split()
                if len(parts) >= 2:
                    if parts[0] == "MD" and len(parts) >= 3:
                        first_names.append(parts[1])  # Use ASTAFAR for MD ASTAFAR
                    else:
                        first_names.append(parts[0])
        return list(set(first_names))  # Remove duplicates
    
    def can_place_word(self, word: str, row: int, col: int, direction: str) -> bool:
        """Check if a word can be placed at given position"""
        if direction == 'horizontal':
            # Check if word fits horizontally
            if col + len(word) > self.width:
                return False
            
            # Check space before word (if not at edge)
            if col > 0 and self.grid[row][col - 1] != ' ':
                return False
            
            # Check space after word (if not at edge)
            if col + len(word) < self.width and self.grid[row][col + len(word)] != ' ':
                return False
            
            # Check each character position and adjacent cells
            for i, char in enumerate(word):
                current_pos = col + i
                current_char = self.grid[row][current_pos]
                
                # If position is occupied, must match exactly
                if current_char != ' ' and current_char != char:
                    return False
                
                # If placing a new character, check vertical neighbors
                if current_char == ' ':
                    # Check cell above
                    if row > 0 and self.grid[row - 1][current_pos] != ' ':
                        return False
                    # Check cell below  
                    if row + 1 < self.height and self.grid[row + 1][current_pos] != ' ':
                        return False
        
        elif direction == 'vertical':
            # Check if word fits vertically
            if row + len(word) > self.height:
                return False
            
            # Check space before word (if not at edge)
            if row > 0 and self.grid[row - 1][col] != ' ':
                return False
            
            # Check space after word (if not at edge)
            if row + len(word) < self.height and self.grid[row + len(word)][col] != ' ':
                return False
            
            # Check each character position and adjacent cells
            for i, char in enumerate(word):
                current_pos = row + i
                current_char = self.grid[current_pos][col]
                
                # If position is occupied, must match exactly
                if current_char != ' ' and current_char != char:
                    return False
                
                # If placing a new character, check horizontal neighbors
                if current_char == ' ':
                    # Check cell to the left
                    if col > 0 and self.grid[current_pos][col - 1] != ' ':
                        return False
                    # Check cell to the right
                    if col + 1 < self.width and self.grid[current_pos][col + 1] != ' ':
                        return False
        
        return True
    
    def place_word(self, word: str, row: int, col: int, direction: str) -> bool:
        """Place a word in the grid"""
        if not self.can_place_word(word, row, col, direction):
            return False
        
        if direction == 'horizontal':
            for i, char in enumerate(word):
                self.grid[row][col + i] = char
        elif direction == 'vertical':
            for i, char in enumerate(word):
                self.grid[row + i][col] = char
        
        self.placed_words.append((word, row, col, direction))
        self.word_positions[word] = (row, col, direction)
        return True
    
    def find_intersections(self, word: str, placed_words: List[Tuple]) -> List[Tuple]:
        """Find possible intersections with already placed words"""
        intersections = []
        
        for placed_word, p_row, p_col, p_direction in placed_words:
            # Find common characters
            for i, char1 in enumerate(word):
                for j, char2 in enumerate(placed_word):
                    if char1 == char2:
                        # Calculate position for intersection
                        if p_direction == 'horizontal':
                            # Place current word vertically intersecting at this character
                            new_row = p_row - i
                            new_col = p_col + j
                            new_direction = 'vertical'
                        else:
                            # Place current word horizontally intersecting at this character
                            new_row = p_row + j
                            new_col = p_col - i
                            new_direction = 'horizontal'
                        
                        # Check bounds
                        if (0 <= new_row < self.height and 0 <= new_col < self.width):
                            # Additional check: ensure this creates a valid crossword intersection
                            if self.is_valid_intersection(word, new_row, new_col, new_direction, placed_word, p_row, p_col, p_direction, i, j):
                                intersections.append((new_row, new_col, new_direction))
        
        return intersections
    
    def is_valid_intersection(self, word: str, row: int, col: int, direction: str, 
                            placed_word: str, p_row: int, p_col: int, p_direction: str, 
                            word_char_idx: int, placed_char_idx: int) -> bool:
        """Check if intersection creates a valid crossword (words cross at exactly one point)"""
        # The intersection should be at exactly one character
        if direction == 'horizontal' and p_direction == 'vertical':
            intersect_row = row
            intersect_col = p_col
            # Check that the intersection is at the expected indices
            if intersect_row == p_row + placed_char_idx and intersect_col == col + word_char_idx:
                return True
        elif direction == 'vertical' and p_direction == 'horizontal':
            intersect_row = p_row
            intersect_col = col
            # Check that the intersection is at the expected indices
            if intersect_row == row + word_char_idx and intersect_col == p_col + placed_char_idx:
                return True
        
        return False
    
    def generate_crossword(self, names: List[str]) -> None:
        """Generate the crossword puzzle"""
        # Sort names by length (longer first for better placement)
        names = sorted(names, key=len, reverse=True)
        
        # Place first word in center
        if names:
            first_word = names[0]
            start_row = self.height // 2
            start_col = (self.width - len(first_word)) // 2
            self.place_word(first_word, start_row, start_col, 'horizontal')
        
        # Place remaining words
        for word in names[1:]:
            placed = False
            
            # Try to intersect with existing words
            intersections = self.find_intersections(word, self.placed_words)
            random.shuffle(intersections)
            
            for row, col, direction in intersections:
                if self.can_place_word(word, row, col, direction):
                    self.place_word(word, row, col, direction)
                    placed = True
                    break
            
            # If can't intersect, try random placement
            if not placed:
                attempts = 100
                while attempts > 0 and not placed:
                    row = random.randint(0, self.height - 1)
                    col = random.randint(0, self.width - 1)
                    direction = random.choice(['horizontal', 'vertical'])
                    
                    if self.can_place_word(word, row, col, direction):
                        self.place_word(word, row, col, direction)
                        placed = True
                        break
                    
                    attempts -= 1
    
    def print_grid(self):
        """Print the grid with border"""
        print("+" + "-" * self.width + "+")
        for row in self.grid:
            print("|" + "".join(row) + "|")
        print("+" + "-" * self.width + "+")
    
    def print_word_list(self):
        """Print the list of placed words"""
        print(f"\nPlaced words ({len(self.placed_words)}):")
        for word, row, col, direction in self.placed_words:
            print(f"  {word} - Row {row+1}, Col {col+1} ({direction})")

# Your class names
class_names = [
    "MD ASTAFAR ALAM",
    "MILAN ARJEL",
    "MILAN POKHAREL", 
    "MITHUN YADAV",
    "NIGAM YADAV",
    "NISHAN BHATTARAI",
    "POOJA RANA",
    "PRASANGA NIRAULA",
    "PRIYANKA KUMARI MISHRA",
    "RAHUL KUMAR ROUNIYAR",
    "RAJAT PRADHAN",
    "RAJAT CHANDRA JHA",
    "RAJESH PANDEY",
    "RAM CHANDRA GHIMIRE",
    "RANJIT ADHIKARI",
    "RATAN THAPA",
    "RAVI PANDIT",
    "RESHMI JHA",
    "RIJAN KARKI",
    "RITESH SAHANI",
    "RITIKA NIRAULA",
    "ROHAN KUMAR SHAH",
    "ROSHAN KARKI",
    "SAGAR KATUWAL",
    "SAMIR BIDARI",
    "SANAM BASTOLA",
    "SANDEEP POUDEL",
    "SANDESH POKHAREL",
    "SANDHYA SHRESTHA",
    "SANGYOG PURI",
    "SANSKAR RIJAL",
    "SAURAV KHANAL",
    "SHUVKANT CHAUDHARY PHANAIT",
    "SHYAM KRISHNA GUPTA",
    "SNEHA PATEL",
    "SONU KUMAR GUPTA",
    "SONY KUMARI CHAUDHARY",
    "SPANDAN GURAGAIN",
    "SUBASH KUMAR YADAV",
    "SUDESH SUBEDI",
    "SUJAN GYAWALI",
    "SUJAN NAINAWASTI",
    "SUJIT KUMAR DAS",
    "SUVASH GIRI",
    "TAYAMA KIRATI",
    "VISION PEER CHAUDHARY",
    "YAM NATH GURAGAIN",
    "YAMRAJ KHADKA"
]

# Create and generate crossword
crossword = NameCrossword(width=60, height=35)
first_names = crossword.extract_first_names(class_names)

print("First names extracted:")
for name in sorted(first_names):
    print(f"  {name}")

crossword.generate_crossword(first_names)

crossword.print_grid()
