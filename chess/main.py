import pygame

from enum import Enum
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

class Piece(pygame.sprite.Sprite):
    def __init__(self, pieceColor: PieceColor, pieceType: PieceType, pos: (int, int), callback):
        super().__init__()
        self.color = pieceColor
        self.type = pieceType
        self.position = pos
        img = pygame.image.load(IMAGE_PATH / Path(pieceColor.value + "-" + pieceType.value + ".png")).convert_alpha()
        self.image = pygame.transform.smoothscale(img, (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect(topleft=(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE))
        self.callback = callback

    def getPosition(self) -> (int, int):
        return self.position

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.callback(self)

class Board:
    def __init__(self):
        pygame.display.set_caption("Chess")
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        self.selectedPiece = None
        self.pieces = self.placePieces()
        
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

        pieces = pygame.sprite.Group()
        for pieceType, positions in startingPositions.items():
            for pos in positions:
                _, y = pos
                color = PieceColor.WHITE if y > 3 else PieceColor.BLACK
                pieces.add(Piece(color, pieceType, pos, self.selectPiece))
        return pieces

    def drawGrid(self):
        self.screen.fill((0,0,0))
        if self.selectedPiece is not None:
            selectedPos = self.selectedPiece.getPosition()
        else:
            selectedPos = (-1, -1)
        p, q = selectedPos
        for i, x in enumerate(range(0, SCREEN_SIZE, CELL_SIZE)):
            for j, y in enumerate(range(0, SCREEN_SIZE, CELL_SIZE)):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                if i == p and j == q:
                    pygame.draw.rect(surface=self.screen, color=(255,0,0), rect=rect)
                elif (i + j) % 2 == 0:
                    pygame.draw.rect(surface=self.screen, color=(210,210,210), rect=rect)
                  
    def draw(self):
        self.drawGrid()
        self.pieces.draw(surface=self.screen)

    def update(self, events: pygame.event):
        self.pieces.update(events)

    def selectPiece(self, piece: Piece):
        self.selectedPiece = piece

def main() -> None:
    pygame.init()
    clock = pygame.time.Clock()
    board = Board()

    # Game Loop
    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        board.update(events)
        
        board.draw()
        pygame.display.update()
        clock.tick(60)      

if __name__ == "__main__":
    main()
