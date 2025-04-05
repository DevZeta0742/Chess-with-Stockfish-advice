from stockfish import Stockfish
from selenium import webdriver
from selenium.webdriver.common.by import By
import chess
import json
import time


with open('stockfish_config.json', 'r') as f:
    config = json.load(f)

stockfish = Stockfish(
    path = r"C:\Users\stockfish\stockfish-windows-x86-64-avx2.exe",
    depth = 18,
    parameters = {"Threads": 2, "Minimum Thinking Time": 30}
)

stockfish.update_engine_parameters(config)

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options = chrome_options)
driver.get("https://www.chess.com/live")


def get_chess_moves():
    """Chess.com의 현재 기보를 가져와서 리스트로 반환"""
    move_elements = driver.find_elements(By.CSS_SELECTOR, "span.node-highlight-content")
    moves = [m.text.strip() for m in move_elements if m.text.strip()]
    return moves

def convert_san_to_uci(san_moves):  # 이거 없으면 기보 못읽어옴
    board = chess.Board()
    uci_moves = []

    for san in san_moves:
        try:
            move = board.parse_san(san)
            uci_moves.append(move.uci())
            board.push(move)

        except Exception as e:
            print(f"failed: {san} - {e}")
            break

    return uci_moves

def main():
    print("Stockfish recommendation sys on")
    prev_moves = []

    while True:
        moves = get_chess_moves()

        if not moves or moves == prev_moves:
            time.sleep(2)
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
