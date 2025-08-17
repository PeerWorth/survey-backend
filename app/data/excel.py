import pandas as pd


def create_excel(data: list, path: str, columns: list[str]) -> None:
    df = pd.DataFrame(data, columns)
    df.to_excel(path, index=False)
    return


def load_excel(path: str) -> list[tuple]:
    df = pd.read_excel(path, engine="openpyxl")
    return [tuple(row) for row in df.itertuples(index=False, name=None)]
