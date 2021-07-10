import itertools
import random


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for _ in range(height):
            row = []
            for _ in range(width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell: tuple[int, int]):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return tuple(self.cells)
        else:
            return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return tuple(self.cells)
        else:
            return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        if not cell in self.safes:
            self.safes.add(cell)
            for sentence in self.knowledge:
                sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        self.add_neighbour_mines_knowledge(cell, count)
        self.mark_safe_and_mine()
        self.extract_from_problem()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        try:
            return (self.safes - self.moves_made).pop()
        except Exception:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        choice = []
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.mines and (i, j) not in self.moves_made:
                    choice.append((i, j))

        try:
            return random.choice(choice)
        except:
            return None

    def add_neighbour_mines_knowledge(self, cell, count):
        """
        It will add sentence to the knowledge that contains neighbour non-safe
        cells and count of mine passed to it.
        """
        neighbour_cells = []
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if 0 <= i < self.height and 0 <= j < self.width:
                    current_cell = (i, j)
                    if current_cell in self.mines:
                        count -= 1
                    elif not current_cell in [*self.moves_made, *self.safes]:
                        neighbour_cells.append(current_cell)
        self.knowledge.append(Sentence(neighbour_cells, count))

    def mark_safe_and_mine(self):
        """
        This method checks if any new mine or safe cell can be found by sentences
        in knowledge
        """
        flag = True
        while flag:
            flag = False
            for sentence in self.knowledge.copy():
                mines = sentence.known_mines()
                safes = sentence.known_safes()
                if mines or safes:
                    self.knowledge.remove(sentence)
                    flag = True
                if mines:
                    for mine in mines:
                        self.mark_mine(mine)
                if safes:
                    for safe in safes:
                        self.mark_safe(safe)
        for sentence in self.knowledge.copy():
            if sentence.cells == set([]):
                self.knowledge.remove(sentence)

    def extract_from_problem(self):
        """
        This method extracts new infomation from given knowledge by using concept
        of subset.
        """
        self.remove_same_sentence()
        knowledge_subset_list = []
        remove_sentence = []
        flag = False
        for (k1, k2) in itertools.permutations(self.knowledge, 2):
            s1, s2 = k1.cells, k2.cells
            if s1.issubset(s2):
                knowledge_subset_list.append((k1, k2))
                remove_sentence.append(k2)
                flag = True

        for (k1, k2) in knowledge_subset_list:
            s = k2.cells - k1.cells
            c = k2.count - k1.count
            self.knowledge.append(Sentence(s, c))

        for sentence in remove_sentence:
            if sentence in self.knowledge:
                self.knowledge.remove(sentence)

        if flag:
            self.mark_safe_and_mine()
            self.extract_from_problem()

    def remove_same_sentence(self):
        """
        This method makes sure that knowledge must have unique sentences.
        """
        new_knowledge = []
        for sentence in self.knowledge:
            if sentence not in new_knowledge:
                new_knowledge.append(sentence)

        self.knowledge = new_knowledge
