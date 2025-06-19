import chess


def convert_san_to_uci(san_moves: list[str], start_fen: str = chess.STARTING_FEN) -> list[str]:
    try:
        board = chess.Board(start_fen)

    except ValueError:
        print(f"[!] Invalid FEN: {start_fen}. Using the standard chess board.")
        board = chess.Board()

    uci_moves = []
    for san in san_moves:
        try:
            move = board.parse_san(san)
            uci_moves.append(move.uci())
            board.push(move)

        except chess.IllegalMoveError as e:
            print(f"[!] Failed to convert SAN '{san}' to UCI (Illegal move): {e}")
            pass

        except Exception as e:
            print(f"[!] An exception occurred while processing SAN '{san}': {e}")
            continue

    return uci_moves
