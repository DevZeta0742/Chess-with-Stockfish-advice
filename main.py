import json
import time
from engine_handler import EngineHandler
from web_handler import WebHandler
import chess_utils
from selenium.common.exceptions import WebDriverException


def main():
    with open('stockfish_config.json', 'r') as f:
        config = json.load(f)

    try:
        engine = EngineHandler(
            path=r"",
            parameters={"Threads": 3, "Minimum Thinking Time": 30}
        )
        engine.update_parameters(config)

        web = WebHandler()
        web.open_page("https://www.chess.com/live")

    except Exception as e:
        print(f"[!] A critical error occurred during initialization: {e}")
        return

    print("=" * 20)
    print("Sys Started")
    print("Waiting for moves...")
    print("=" * 20)

    prev_moves_str = ""
    start_fen = None

    try:
        while True:
            if start_fen is None:
                is_960 = config.get("UCI_Chess960", "false").lower() == "true"
                if is_960:
                    start_fen = ''  # 공유버튼을 누르고 PGN에 들어가면 FEN이 나오는데, 그거 복붙
                    print(f"[INFO] Chess960 detected. start_fen : {start_fen}")
                else:
                    start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
                    print(f"[INFO] Standard chess mode. start_fen : {start_fen}", start_fen)

            moves = web.get_chess_moves()
            current_moves_str = ' '.join(moves)

            if not moves or current_moves_str == prev_moves_str:
                time.sleep(0.1)
                continue

            prev_moves_str = current_moves_str

            uci_moves = chess_utils.convert_san_to_uci(moves, start_fen)

            engine.set_position(uci_moves)
            top_moves = engine.get_top_moves(4)

            print("\n" + "=" * 50)
            print(f"Detected moves ({len(moves)}): {current_moves_str}")
            print("Recommendations (Top 4):")

            for move in top_moves:
                info = f" - {move['Move']} | Eval: "
                if move.get("Centipawn") is not None:
                    info += f"{move['Centipawn']} cp "

                if move.get("Mate") is not None:
                    info += f"M{abs(move['Mate'])}"

                print(info)

            print("=" * 50)
            time.sleep(0.1)

    except WebDriverException as e:
        print(f"[!] WebDriver error: {e}. Please check the browser session.")

    except KeyboardInterrupt:
        print("\n[!] Program terminated by user.")

    except Exception as e:
        print(f"[!] An unhandled exception occurred: {e}")

    finally:
        print("[+] Shut Down")
        web.close()


if __name__ == "__main__":
    main()
