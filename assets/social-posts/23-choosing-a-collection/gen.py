import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from single_image_template import single_image

OUT = os.path.dirname(__file__)

single_image(
    os.path.join(OUT, "image.png"),
    "Concept",
    "Picking The Right Collection",
    [
        ("List", "Ordered, changeable — the default bag of things"),
        ("Tuple", "Ordered, fixed — hashable, works as a dict key"),
        ("Set", "Unique values only — O(1) avg membership check"),
        ("Dict", "Lookup by key — the structured-data workhorse"),
    ],
    "if x in my_set:  # O(1) avg, vs O(n) for a list",
)

print("done: 23")
