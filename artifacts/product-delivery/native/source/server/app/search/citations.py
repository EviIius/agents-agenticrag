import re
from collections.abc import Callable

CODE = re.compile(r"(```[\s\S]*?(?:```|$)|`[^`\n]*`)")


def outside_code(text: str, transform: Callable[[str], str]) -> str:
    return "".join(part if i % 2 else transform(part) for i, part in enumerate(CODE.split(text)))


def normalize(text: str, n: int) -> str:
    def transform(t: str) -> str:
        t = re.sub(r"【(\d+)(?:†[^】]*)?】", r"[\1]", t)
        t = re.sub(r"\[\^(\d+)\]", r"[\1]", t)
        t = re.sub(r"\[(?:source|src|s)\s*:?\s*(\d+)\]", r"[\1]", t, flags=re.I)
        t = re.sub(r"\((?:source|src)\s*:?\s*(\d+)\)", r"[\1]", t, flags=re.I)
        t = re.sub(
            r"\[(\d+(?:\s*[,;]\s*\d+)+)\]",
            lambda m: "".join("[" + v.strip() + "]" for v in re.split(r"[,;]", m[1])),
            t,
        )
        t = re.sub(
            r"\[(\d+)\s*[-–]\s*(\d+)\]",
            lambda m: (
                "".join(f"[{i}]" for i in range(int(m[1]), int(m[2]) + 1))
                if 0 <= int(m[2]) - int(m[1]) <= 9
                else m[0]
            ),
            t,
        )
        t = re.sub(r"\s?\[(\d+)\](?!\()", lambda m: m[0] if 1 <= int(m[1]) <= n else "", t)
        while True:
            replaced = re.sub(r"\[(\d+)\]\[\1\](?!\()", r"[\1]", t)
            if replaced == t:
                return t
            t = replaced

    return outside_code(text, transform)


def cited(text: str) -> set[int]:
    ids: set[int] = set()

    def collect(t: str) -> str:
        ids.update(int(m[1]) for m in re.finditer(r"\[(\d+)\](?!\()", t))
        return t

    outside_code(text, collect)
    return ids
