#!/usr/bin/env python3

from dataclasses import dataclass


@dataclass
class Config:
    window_title: str
    title_font: str
    body_font: str
