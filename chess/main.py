import pygame

from enum import Enum
from dataclasses import dataclass
from pathlib import Path

SCREEN_SIZE = 800
CELL_SIZE = int(SCREEN_SIZE / 8)

IMAGE_PATH = Path(__file__).parent.resolve() / Path("assets")

class PieceColor(Enum):
    WHITE = "white"
    BLACK = "black"

class PieceType(Enum):
    PAWN = "pawn"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    QUEEN = "queen"
    KING = "king"

@dataclass
class Piece:
    def __init__(self, pieceColor: PieceColor, pieceType: PieceType, pos: (int, int)):
        self.color = pieceColor
        self.type = pieceType
        self.position = pos
        img = pygame.image.load(IMAGE_PATH / Path(pieceColor.value + "-" + pieceType.value + ".png")).convert_alpha()
        self.image = pygame.transform.smoothscale(img, (CELL_SIZE, CELL_SIZE))

    def draw(self, surface: pygame.Surface):
        x, y = self.position
        surface.blit(self.image, (x*CELL_SIZE, y*CELL_SIZE))

class Board:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        self.clock = pygame.time.Clock()
        self.pieces = []
        pygame.display.set_caption("Chess")

    def drawGrid(self):
        self.screen.fill((0,0,0))
        for i, x in enumerate(range(0, SCREEN_SIZE, CELL_SIZE)):
            for j, y in enumerate(range(0, SCREEN_SIZE, CELL_SIZE)):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                if (i + j) % 2 == 0:
                    pygame.draw.rect(surface=self.screen, color=(210,210,210), rect=rect)
                
    def placePieces(self):
        def getQuad(coord):
            x, y = coord
            return [(x,y),(x,7-y),(7-x,y),(7-x,7-y)]
        
        def getRow(y):
            cells = []
            for x in range(8):
                cells.append((x,y))
            return cells

        startingPositions = {
            PieceType.ROOK: getQuad((0,0)),
            PieceType.KNIGHT: getQuad((1,0)),
            PieceType.BISHOP: getQuad((2,0)),
            PieceType.PAWN: getRow(1) + getRow(6),
            PieceType.QUEEN: [(4,0),(3,7)],
            PieceType.KING: [(3,0),(4,7)],
        }

        for pieceType, positions in startingPositions.items():
            for pos in positions:
                _, y = pos
                color = PieceColor.WHITE if y > 3 else PieceColor.BLACK
                self.pieces.append(Piece(color, pieceType, pos))

    def drawPieces(self):
        for piece in self.pieces:
            piece.draw(surface=self.screen)


def main() -> None:
    board = Board()
    board.drawGrid()
    board.placePieces()
    board.drawPieces()

    # Game Loop
    running = True
    while running:
        mouse = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True

        pygame.display.update()        

if __name__ == "__main__":
    main()
