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

    def setPosition(self, pos: (int, int)):
        x, y = pos
        if 0 <= x < 8 and 0 <= y < 8:
            self.position = pos
            self.rect.topleft = (x * CELL_SIZE, y * CELL_SIZE)
    
    def getColor(self) -> PieceColor:
        return self.color

    def getType(self) -> PieceType:
        return self.type

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.callback(self)

class Board:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        self.selectedPiece = None
        self.turn = (0, PieceColor.WHITE)
        self.pieces = self.placePieces()
        self.setBanner()
        
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
            PieceType.QUEEN: [(3,0),(3,7)],
            PieceType.KING: [(4,0),(4,7)],
        }

        pieces = pygame.sprite.Group()
        for pieceType, positions in startingPositions.items():
            for pos in positions:
                _, y = pos
                color = PieceColor.WHITE if y > 3 else PieceColor.BLACK
                pieces.add(Piece(color, pieceType, pos, self.selectPiece))
        return pieces

    def pieceAt(self, pos: (int, int)) -> Piece | None:
        for piece in self.pieces:
            if piece.getPosition() == pos:
                return piece
        return None

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
        def pixelToCell(pos: (int, int)) -> (int, int):
            x, y = pos
            return(x // CELL_SIZE, y // CELL_SIZE)

        self.pieces.update(events)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                cell = pixelToCell(event.pos)
                if self.selectedPiece is not None and cell != self.selectedPiece.getPosition():
                    self.move(cell)

    def selectPiece(self, piece: Piece):
        _, turnColor = self.turn
        if piece.getColor() == turnColor:
            self.selectedPiece = piece

    def iterTurn(self):
        num, color = self.turn
        if color == PieceColor.WHITE:
            self.turn = (num, PieceColor.BLACK)
        else:
            self.turn = (num + 1, PieceColor.WHITE)
        self.setBanner()

    def setBanner(self):
        pygame.display.set_caption(f"Chess | {self.turn[0] + 1} | {self.turn[1].value}")

    def move(self, target: (int, int)):
        piece = self.selectedPiece
        if piece is None:
            return
        pos = piece.getPosition()

        takeablePiece = self.pieceAt(target)
        if takeablePiece is not None and takeablePiece.getColor() is piece.getColor():
            takeablePiece = None
        
        def isLegal() -> bool:
            x, y = pos
            p, q = target
            dx, dy = abs(p-x), abs(q-y)
            if dx + dy == 0:
                return False

            def isObstructed() -> bool:
                if piece.getType() == PieceType.KNIGHT:
                    return False
                sx = 0 if p == x else (1 if p > x else -1)
                sy = 0 if q == y else (1 if q > y else -1)
                cx, cy = x + sx, y + sy
                while (cx, cy) != target:
                    if self.pieceAt((cx, cy)):
                        return True
                    cx += sx
                    cy += sy
                return False

            if isObstructed():
                return False

            match piece.getType():
                case PieceType.ROOK:
                    return (dx == 0 or dy == 0)
                case PieceType.KNIGHT:
                    return (dx + dy == 3 and dx < 3 and dy < 3)
                case PieceType.BISHOP:
                    return (dx == dy)
                case PieceType.PAWN:
                    isWhite = piece.getColor() == PieceColor.WHITE
                    if not 0 < dy <= 2:
                        return False
                    if (q > y) if isWhite else (q < y):
                        return False
                    if dy > 1 and (y != 6 if isWhite else y != 1):
                        return False
                    if dx > 0 and takeablePiece is None:
                        return False
                    return True
                case PieceType.QUEEN:
                    return (dx == dy or dx == 0 or dy == 0)
                case PieceType.KING:
                    return(dx <= 1 and dy <= 1)
            return False

        if isLegal():
            if takeablePiece is not None:
                self.pieces.remove(takeablePiece)
            self.selectedPiece.setPosition(target)
            self.iterTurn()

        self.selectedPiece = None

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

    pygame.quit()

if __name__ == "__main__":
    main()
