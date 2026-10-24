"""Design tokens for the deck: one place to restyle everything.

Colour carries meaning across the deck:
  TEAL  = asserted data (what a source said)
  AMBER = inferred data (what the model lets us conclude)
  CLAY  = warnings, traps and antipatterns
"""

from pptx.dml.color import RGBColor

# Canvas (16:9, inches)
SLIDE_W = 13.333
SLIDE_H = 7.5
MARGIN = 0.6
CONTENT_TOP = 1.75
CONTENT_BOTTOM = 6.85

# Palette
INK = RGBColor(0x17, 0x27, 0x2E)       # dark slides, body text
INK_SOFT = RGBColor(0x24, 0x38, 0x40)  # cards on dark slides
TEAL = RGBColor(0x1F, 0x7A, 0x6D)      # asserted / primary
TEAL_DARK = RGBColor(0x15, 0x5E, 0x54)
MINT = RGBColor(0x7F, 0xD1, 0xC1)      # teal on dark backgrounds
MINT_SOFT = RGBColor(0xC6, 0xE8, 0xE0)
AMBER = RGBColor(0xE0, 0x95, 0x2B)     # inferred / accent
AMBER_TINT = RGBColor(0xFC, 0xF1, 0xDF)
CLAY = RGBColor(0xC2, 0x4E, 0x36)      # warnings
CLAY_TINT = RGBColor(0xF8, 0xE4, 0xDF)
MIST = RGBColor(0xEA, 0xF3, 0xF0)      # card fill on light slides
LINE = RGBColor(0xC9, 0xD8, 0xD4)      # hairlines, table rules
MUTED = RGBColor(0x5B, 0x6B, 0x70)     # captions
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# Code panel
CODE_BG = RGBColor(0x1C, 0x29, 0x2F)
CODE_TEXT = RGBColor(0xE3, 0xEB, 0xEE)
CODE_COMMENT = RGBColor(0x86, 0x9A, 0xA0)
CODE_STRING = RGBColor(0xB5, 0xD9, 0x8F)
CODE_KEYWORD = RGBColor(0xF2, 0xB8, 0x66)
CODE_VAR = MINT
CODE_PNAME = RGBColor(0xA8, 0xCF, 0xF0)
CODE_IRI = RGBColor(0x9A, 0xB0, 0xB8)

# Typography
HEAD_FONT = "Cambria"
BODY_FONT = "Calibri"
CODE_FONT = "Consolas"

TITLE_PT = 34
KICKER_PT = 13
BODY_PT = 16
CARD_TITLE_PT = 18
CARD_BODY_PT = 14
CODE_PT = 13
CAPTION_PT = 11

DECK_FOOTER = "What is an ontology? · from RDF to OWL"


def hex_of(color: RGBColor) -> str:
    return str(color)


# Theme colours written into the .pptx so edits in PowerPoint stay on palette.
THEME_COLORS = {
    "dk1": INK,
    "lt1": WHITE,
    "dk2": TEAL_DARK,
    "lt2": MIST,
    "accent1": TEAL,
    "accent2": AMBER,
    "accent3": CLAY,
    "accent4": MINT,
    "accent5": RGBColor(0x5B, 0x8F, 0xA8),
    "accent6": MUTED,
    "hlink": TEAL,
    "folHlink": TEAL_DARK,
}
