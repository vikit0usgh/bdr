import json
from pathlib import Path

from models.collection import Collection


class CollectionService:

    @staticmethod
    def save(collection: Collection, path: str | Path) -> None:
        path = Path(path)

        with path.open("w", encoding="utf-8") as file:
            json.dump(
                collection.to_dict(),
                file,
                indent=4,
                ensure_ascii=False,
            )

    @staticmethod
    def load(path: str | Path) -> Collection:
        path = Path(path)

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return Collection.from_dict(data)
