"""
Minesweeper
This is a classic game known as Minesweeper where the goal is to clear the play
area of safe squares. If a square with a mine is clicked, the game ends.
Left click reveals a square (safe or mine) and right click adds a flag to
square which prevents accidentally clicking on it.
Empty squares will reveal all adjacent empty squares and border squares just
like in the original game. Also clicking on an already revealed square will
reveal adjacent squares if there are a right number of flags around it. This
will fail the game if flags are in incorrect positions.
The number on the top left shows how many mines there are left and the number
on top right shows how many safe squares are unrevealed. The spinbox on the top
can be used to adjust the amount of mines.
"""
from tkinter import *
import random

IMAGE_FILES = ['0.png', '1.png', '2.png', '3.png', '4.png', '5.png', '6.png',
               '7.png', '8.png', 'bomb.png', 'empty.png', 'flagged.png',
               'explodedBomb.png']


class Minesweeper:
    def __init__(self):
        self.__squares = []
        self.__square_coordinates = {}
        self.__marked_squares = []
        self.__activated_squares = []
        self.__mine_squares = []
        self.__size = 10
        self.__undiscovered_mines = self.__size
        self.__main_window = Tk()
        self.__images = []
        for image in IMAGE_FILES:
            new_image = PhotoImage(file=f"images/{image}")
            self.__images.append(new_image)
        self.__mines_label = Label(self.__main_window,
                                   text=self.__undiscovered_mines,
                                   font=("Default", 25))
        self.__mines_label.grid(row=0, column=0)
        self.__undiscovered_squares = Label(self.__main_window,
                                            text=self.__undiscovered_mines ** 2
                                            , font=("Default", 25))
        self.__undiscovered_squares.grid(row=0, column=self.__size - 1)
        self.__restart_button = Button(self.__main_window,
                                       text="Restart", command=self.start_game)
        self.__restart_button.grid(row=0, column=2)
        self.__current_mode = "Reveal"
        self.__ending_text = Label(self.__main_window, text="",
                                   font=("Default", 20))
        self.__ending_text.grid(row=0, column=self.__size - 5,
                                columnspan=3, padx=30)
        self.__mines_amount = Spinbox(self.__main_window, from_=0,
                                      to=self.__size ** 2 - 1, width=3,
                                      wrap=True)
        self.__mines_amount.grid(row=0, column=4)
        self.__mines_amount.insert(0, 1)
        # Set spinbox to readonly after inserting the right value
        self.__mines_amount.configure(state='readonly')
        self.start_game()
        self.__main_window.mainloop()

    def get_square(self, x, y):
        """
        Gets a square with given coordinates
        :param x: int, x-coordinate
        :param y: int, y-coordinate
        :return: Label, The wanted square, None if incorrect coordinates are
        given
        """
        # If either index is outside of the game
        if y >= self.__size or x >= self.__size or y < 0 or x < 0:
            return None
        # Find index
        index = y * self.__size + x
        square = self.__squares[index]
        return square

    def mark_square(self, x, y):
        """
        Toggles a flag in a square with given coordinates
        :param x: int, x-coordinate
        :param y: int, y-coordinate
        :return: nothing
        """
        square = self.get_square(x, y)
        # If square is activated, do nothing
        if square in self.__activated_squares:
            return
        # Get the old amount of mines
        old_value = self.__mines_label.cget("text")
        # If square is marked, unmark it
        if square in self.__marked_squares:
            self.__marked_squares.remove(square)
            square.configure(image=self.__images[10])
            # Update value
            self.__mines_label.configure(text=old_value + 1)
        # Prevents using too many flags
        elif old_value > 0:
            self.__marked_squares.append(square)
            square.configure(image=self.__images[11])
            self.__mines_label.configure(text=old_value - 1)

    def activate_square(self, x, y, check_adjacent=True):
        """
        Activates a given square
        :param x: int, x-coordinate
        :param y: int, y-coordinate
        :param check_adjacent: bool, If False is given, will not check adjacent
        squares. Used while ending the game
        :return: nothing
        """
        # If it's the first square to be clicked, find its index and exclude
        # it from mines which prevents losing on the first turn
        if len(self.__activated_squares) == 0:
            # Indexes go from left to right from top to bottom
            index = y * self.__size + x
            self.generate_mines(index)
        square = self.get_square(x, y)
        # Check if square is marked or activated and if it is, do nothing
        if square in self.__marked_squares:
            return
        # Check if square has the right amount of flags around it and activate
        # adjacent squares if there are
        # Will fail the game if flags are in incorrect positions
        elif square in self.__activated_squares:
            mines, flags = self.calculate_mines_and_flags(square)
            if mines == flags:
                self.activate_adjacent_squares(square)
            return
        self.__activated_squares.append(square)
        # If square is a mine, end the game
        if square in self.__mine_squares:
            # If the game hasn't ended set current mine to exploded mine
            # Use check_adjacent parameter as it's set to False after the game
            # ends
            if check_adjacent:
                square.configure(image=self.__images[12])
            else:
                # If the game already ended, set the rest of the mines to
                # normal mines
                square.configure(image=self.__images[9])
            self.end_game("You lose")
        # If square is safe, reveal it
        else:
            self.__undiscovered_squares.configure(
                text=self.__undiscovered_squares.cget("text") - 1)
            # Calculate mines
            mines, _ = self.calculate_mines_and_flags(square)
            square.configure(image=self.__images[mines])
            # If square has no mines next to it, reveal empty squares nearby
            if mines == 0 and check_adjacent:
                self.activate_adjacent_squares(square)
            # Check for win after every successful click
            self.check_win()

    def calculate_mines_and_flags(self, square):
        """
        Calculates how many mines and flags there are around a given square
        :param square: Label
        :return: (int, int), Number of mines and flags
        """
        square_coordinates = self.__square_coordinates.get(square)
        row = square_coordinates[0]
        column = square_coordinates[1]
        mines = 0
        flags = 0
        # Iterate a 3x3 grid around square
        for y in range(column - 1, column + 2):
            for x in range(row - 1, row + 2):
                current_square = self.get_square(x, y)
                if current_square is square:
                    continue
                if current_square in self.__mine_squares:
                    mines += 1
                if current_square in self.__marked_squares:
                    flags += 1
        return mines, flags

    def activate_adjacent_squares(self, square):
        """
        Activates empty adjacent squares
        :param square: Label
        :return: nothing
        """
        square_coordinates = self.__square_coordinates.get(square)
        # Get correct row and column
        row = square_coordinates[0]
        column = square_coordinates[1]
        # Check squares that are adjacent to this square
        for y in range(column - 1, column + 2):
            for x in range(row - 1, row + 2):
                square = self.get_square(x, y)
                if square in self.__activated_squares:
                    continue
                elif square is None:
                    continue
                else:
                    # This will recursively check all nearby squares
                    # Squares that are out of playable area are handled by
                    # get_square later
                    self.activate_square(x, y)

    def end_game(self, message):
        """
        Ends the game with a given message
        :param message: str, Message to show after the ending
        :return: nothing
        """
        # Activate all squares that are left and not marked
        for y in range(self.__size):
            for x in range(self.__size):
                square = self.get_square(x, y)
                if square not in self.__activated_squares:
                    # Don't activate adjacent squares as that would hang the
                    # game
                    self.activate_square(x, y, False)
        self.__ending_text.configure(text=message)
        # Unbind all label actions to stop all further inputs after the game
        # has finished
        for square in self.__squares:
            square.unbind("<Button-1>")
            square.unbind("<Button-2>")
            square.unbind("<Button-3>")

    def check_win(self):
        """
        Checks if player has won and activates the ending
        :return: nothing
        """
        # If there are no unrevealed safe squares left, the player has won
        if self.__undiscovered_squares.cget("text") <= 0:
            self.end_game("You won")

    def generate_mines(self, exclude=-1):
        """
        Randomly generates mines for the game
        :param exclude: int, Index of the square to exclude from mines
        :return: nothing
        """
        # Create a list with all indexes and current square excluded
        list_of_valid_squares = list(range(0, self.__size ** 2))
        list_of_valid_squares.pop(exclude)
        # Choose random squares to have mines in them
        mines = random.sample(list_of_valid_squares, self.__undiscovered_mines)
        # Add right squares to list with mine squares
        for index in mines:
            self.__mine_squares.append(self.__squares[index])

    def start_game(self):
        """
        Starts or restarts the game and sets all the values accordingly
        :return: nothing
        """
        # Delete old squares
        for square in self.__squares:
            square.destroy()
        self.__squares = []
        self.__square_coordinates = {}
        self.__activated_squares = []
        self.__mine_squares = []
        self.__size = 10
        self.__undiscovered_mines = int(self.__mines_amount.get())
        for y in range(self.__size):
            for x in range(self.__size):
                # Add right coordinates to clicks
                # Exclude first argument as it's given automatically and not
                # needed
                def left_click(_, x_coord=x, y_coord=y):
                    self.activate_square(x_coord, y_coord)

                def right_click(_, x_coord=x, y_coord=y):
                    self.mark_square(x_coord, y_coord)

                # Use label as then right click can be used
                new_square = Label(self.__main_window,
                                   height=60, width=60,
                                   image=self.__images[10])
                # Bind left and right mouse buttons
                new_square.bind("<Button-1>", left_click)
                # Some OSes use <Button-2> and some <Button-3> as right click
                # according to the internet
                new_square.bind("<Button-2>", right_click)
                new_square.bind("<Button-3>", right_click)
                new_square.grid(row=y + 1, column=x)
                self.__squares.append(new_square)
                self.__square_coordinates[new_square] = [x, y]
        self.__mines_label.configure(text=self.__undiscovered_mines)
        self.__undiscovered_squares.configure(
            text=self.__size ** 2 - self.__undiscovered_mines)
        self.__ending_text.configure(text="")


def main():
    Minesweeper()


if __name__ == "__main__":
    main()
