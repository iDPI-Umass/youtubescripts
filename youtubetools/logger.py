import os
from datetime import datetime
from config.definitions import ROOT_DIR


def log_error(collection: str, video_id: str, package: str, message: any) -> None:
    with open(os.path.join(ROOT_DIR, "collections", collection, "logs",
                           f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{package}_{video_id}.log"),
              "w") as log:
        log.write(message)
    return
