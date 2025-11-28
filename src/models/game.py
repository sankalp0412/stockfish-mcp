import chess
from chess import Move, Square as chessSquare, Board, InvalidMoveError

from uuid import uuid4
from typing import List
import datetime
from dataclasses import dataclass, field


def get_new_uuid() -> str:
    return str(uuid4())


@dataclass
class Game:
    user_elo: str
    game_id: str = field(default_factory=get_new_uuid)
    moves: List[str] = field(default_factory=list)
    fen: str = field(default=chess.STARTING_FEN)

    def get_game_id(self):
        return str(self.game_id)

    def play_move(self, move: str) -> bool:
        board = chess.Board(fen=self.fen)
        try:
            candidate_move = board.parse_uci(move)
            board.push(candidate_move)
        except (ValueError, chess.InvalidMoveError) as err:
            print(f"Invalid move '{move}': {err}")
            return False
        except Exception as err:
            print(f"Unexpected error while appending move '{move}': {err}")
            return False

        self.moves.append(move)
        self.fen = board.fen()
        return True

    def get_fen(self) -> str:
        return self.fen

    def get_elo(self) -> str:
        return self.user_elo

    def is_move_valid(self, move:str) -> bool:
        board = chess.Board(fen=self.fen)
        try:
            
            uci_move: Move = Move.from_uci(move) 
            return board.is_legal(uci_move)
        except (chess.InvalidMoveError) as err:
            return False
            