from dataclasses import dataclass


@dataclass
class DiffusionCGParams:

    total_step: int

    enable: bool
    sd_ver: str

    rc_str: float
    LUTs: list[float]

    normalization: bool
    dynamic_range: float

    def __bool__(self):
        return self.enable
