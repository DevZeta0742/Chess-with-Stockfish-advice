import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException


class WebHandler:
    def __init__(self):
        options = uc.ChromeOptions()
        user_data_dir = os.path.join(os.getcwd(), "chess_profile")
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")

        self.driver = uc.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

    def open_page(self, url: str):
        self.driver.get(url)

    def get_chess_moves(self) -> list[str]:
        try:
            move_elements = self.driver.find_elements(By.CSS_SELECTOR, "span.node-highlight-content")

            moves = []
            for elem in move_elements:
                move_text = elem.text.strip()
                if move_text:
                    if '. ' in move_text:
                        moves.append(move_text.split('. ')[1])

                    else:
                        moves.append(move_text)

            return moves

        except StaleElementReferenceException:
            print("[!] Stale element detected. Skipping this turn.")
            return []

        except Exception as e:
            print(f"[!] An unexpected error occurred while fetching moves: {e}")
            return []

    def close(self):
        self.driver.quit()
