from stockfish import Stockfish
from selenium import webdriver
from selenium.webdriver.common.by import By
import chess
import json
import time


with open('stockfish_config.json', 'r') as f:
    config = json.load(f)

stockfish = Stockfish(
    path = r" ",  # you should  fill this blank with path to the stockfish.exe you downloaded ( r"C:\ ~ ~ ~ .exe"
    depth = 18,
    parameters = {"Threads": 2, "Minimum Thinking Time": 30}
)

stockfish.update_engine_parameters(config)

chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options = chrome_options)
driver.get("https://www.chess.com/live")


def get_chess_moves():
    """Chess.com의 현재 기보를 가져와서 리스트로 반환"""
    move_elements = driver.find_elements(By.CSS_SELECTOR, "span.node-highlight-content")
    moves = [m.text.strip() for m in move_elements if m.text.strip()]
    return moves


def convert_san_to_uci(san_moves):
    """SAN(Standard Algebraic Notation) 이동을 UCI 형식으로 변환"""
    board = chess.Board()

    if len(san_moves) % 2 != 0:
    board.turn = chess.WHITE

    uci_moves = []

    for san in san_moves:
        try:
            move = board.parse_san(san)
            uci_moves.append(move.uci())
            board.push(move)

        except Exception as e:
            if len(san) == 2 and san[0] in 'abcdefgh' and san[1] in '12345678':
                target_square = chess.parse_square(san)
                possible_moves = []

                for move in board.legal_moves:
                    if move.to_square == target_square:
                        possible_moves.append(move)

                if len(possible_moves) == 1:
                    uci_moves.append(possible_moves[0].uci())
                    board.push(possible_moves[0])
                    print(f"success: {san} → {possible_moves[0].uci()}")
                    continue

                else:
                    print(f"ambiguous move: {san} - multiple pieces can move or move is not possible")

            elif san in ['O-O', '0-0']:
                if board.turn == chess.WHITE:
                    move = chess.Move.from_uci('e1g1')

                else:
                    move = chess.Move.from_uci('e8g8')

                if move in board.legal_moves:
                    uci_moves.append(move.uci())
                    board.push(move)
                    print(f"kingside castling: {san}")

                    continue

                else:
                    print(f"this kingside castling is illegal: {san}")

            elif san in ['O-O-O', '0-0-0']:
                if board.turn == chess.WHITE:
                    move = chess.Move.from_uci('e1c1')

                else:
                    move = chess.Move.from_uci('e8c8')

                if move in board.legal_moves:
                    uci_moves.append(move.uci())
                    board.push(move)
                    print(f"queenside castling: {san}")

                    continue

                else:
                    print(f"this queenside castling is illegal: {san}")

            elif san.startswith('x') and len(san) == 3:
                target_square = chess.parse_square(san[1:3])
                capture_moves = []

                for move in board.legal_moves:
                    if move.to_square == target_square and board.is_capture(move):
                        capture_moves.append(move)

                if len(capture_moves) == 1:
                    uci_moves.append(capture_moves[0].uci())
                    board.push(capture_moves[0])
                    print(f"success: {san} → {capture_moves[0].uci()}")

                    continue

                else:
                    print(f"ambiguous capture move: {san}")

            else:
                print(f"failed to parse: {san} — {e}")

    return uci_moves


def main():
    print("Stockfish recommendation sys on")
    prev_moves = []

    while True:
        moves = get_chess_moves()

        if not moves or moves == prev_moves:
            time.sleep(1)
            continue

        prev_moves = moves.copy()
        uci_moves = convert_san_to_uci(moves)
        stockfish.set_position(uci_moves)
        top_moves = stockfish.get_top_moves(4)

        print("\n" + "=" * 50)
        print("Detecting:", ' '.join(moves))
        print("Recommended (Top 4):")

        for move in top_moves:
            info = f" - {move['Move']} | Evaluation: "
            if "Centipawn" in move and move["Centipawn"] is not None:
                info += f"{move['Centipawn']} cp "

            if "Mate" in move and move["Mate"] is not None:
                info += f"Mate in {abs(move['Mate'])}"

            print(info)

        print("=" * 50)

        time.sleep(0.01)


if __name__ == "__main__":
    main()
