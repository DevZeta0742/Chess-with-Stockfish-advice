from stockfish import Stockfish
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException
import undetected_chromedriver as uc
import chess
import json
import time
import os

with open('stockfish_config.json', 'r') as f:
    config = json.load(f)

stockfish = Stockfish(
    path = r" ",  # you should  fill this blank with path to the stockfish.exe you downloaded ( r"C:\ ~ ~ ~ .exe )"
    depth=18,
    parameters={"Threads": 2, "Minimum Thinking Time": 30}
)

stockfish.update_engine_parameters(config)


def get_chess_moves(driver):
    try:
        move_elements = driver.find_elements(By.CSS_SELECTOR, "span.node-highlight-content")
        moves = []

        for elem in move_elements:
            try:
                text = elem.text.strip()
                if text:
                    moves.append(text)

            except StaleElementReferenceException:
                print("[!] Stale element inside loop. Skipping one move.")
                continue

        return moves

    except StaleElementReferenceException:
        print("[!] Stale element (outer). Skipping all moves this round.")
        return []

    except Exception as e:
        print(f"[!] Unknown error while fetching moves: {e}")
        return []


def convert_san_to_uci(san_moves):
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
            print(f"[!] Failed to parse SAN '{san}': {e}")
            continue

    return uci_moves


def main():
    options = uc.ChromeOptions()
    user_data_dir = os.path.join(os.getcwd(), "chess_profile")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    driver = uc.Chrome(options=options)

    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    driver.get("https://www.chess.com/live")

    print("Stockfish recommendation sys on")
    prev_moves = []

    while True:
        try:
            moves = get_chess_moves(driver)
            if not moves or moves == prev_moves:
                time.sleep(0.3)
                continue

            prev_moves = moves.copy()
            uci_moves = convert_san_to_uci(moves)
            stockfish.set_position(uci_moves)
            top_moves = stockfish.get_top_moves(4)

            print("\n" + "=" * 50)
            print("Detected:", ' '.join(moves))
            print("Recommended (Top 4):")

            for move in top_moves:
                info = f" - {move['Move']} | Evaluation: "
                if "Centipawn" in move and move["Centipawn"] is not None:
                    info += f"{move['Centipawn']} cp "

                if "Mate" in move and move["Mate"] is not None:
                    info += f"Mate in {abs(move['Mate'])}"

                print(info)

            print("=" * 50)
            time.sleep(0.3)

        except StaleElementReferenceException:
            print("[!] Stale element exception caught in main loop. Recovering...")
            time.sleep(0.5)
            continue

        except WebDriverException as e:
            print(f"[!] WebDriver error: {e}. Check Chrome session.")
            break

        except Exception as e:
            print(f"[!] Unhandled exception: {e}")
            time.sleep(1)
            continue


if __name__ == "__main__":
    main()
