from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Tag:
    interpreter: str
    abi: str | None
    platform: str

    def __str__(self) -> str:
        abi = self.abi or "none"
        return f"{self.interpreter}-{abi}-{self.platform}"
