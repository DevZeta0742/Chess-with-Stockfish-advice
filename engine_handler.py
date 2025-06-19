from stockfish import Stockfish


class EngineHandler:
    def __init__(self, path: str, parameters: dict):
        try:
            self.stockfish = Stockfish(path=path, depth=18, parameters=parameters)
            print("[+] Stockfish engine loaded successfully.")

        except Exception as e:
            print(f"[!] Failed to load the Stockfish engine: {e}")
            raise

    def update_parameters(self, config: dict):
        self.stockfish.update_engine_parameters(config)
        is_960 = config.get("UCI_Chess960", "false").lower() == "true"
        print(f"[+] Engine parameters updated successfully. (Chess960 mode: {is_960})")

    def set_position(self, uci_moves: list[str]):
        self.stockfish.set_position(uci_moves)

    def get_top_moves(self, num_moves: int = 4) -> list[dict]:
        return self.stockfish.get_top_moves(num_moves)
