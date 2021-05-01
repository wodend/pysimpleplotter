#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Tuple


@dataclass
class GuiConfig:
    window_title: str
    title_font: Tuple[str, int, str]
    body_font: Tuple[str, int, str]
