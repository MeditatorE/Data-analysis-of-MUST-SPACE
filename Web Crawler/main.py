import time
import logging

import crawler

time_start = int(time.time())
with open(f"./logs/main_{time_start}.log", "w+") as f:
    f.truncate(0)

logging.basicConfig(level = 'DEBUG', format = '[%(asctime)s] [%(levelname)s] %(message)s', encoding = 'utf-8',
                    handlers = [
                        logging.FileHandler(f"./logs/main_{time_start}.log"),
                        logging.StreamHandler()
                    ])

with open(f"./data/failed.txt", "w") as f:
    f.truncate(0)

crawler.crawl_by_range(1, 9999)