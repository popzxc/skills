---
name: sketch-diagram
description: "Create or revise sparse, hand-drawn SVG diagrams and conceptual illustrations, with matching light and dark variants. Use when explicitly invoked."
---

# Sketch Diagram

Draw a simple illustration that helps the reader see the idea. Match a sketch made in Excalidraw or on a whiteboard: hand-drawn linework, a few colors, short labels, and generous space.

## Match the style

View [assets/style-reference.png](assets/style-reference.png) before the first drawing. [Its SVG](assets/style-reference.svg) is available when the source geometry is useful. This is a style reference, not a fixed layout.

- Use code-native SVG with gently uneven outlines, small variations in tilt, bowed connectors, and open arrowheads. Keep the irregularity subtle enough that the drawing stays legible.
- Use the bundled palette: blue and orange for related groups, green and red for meaningful states. Keep the same meaning within a drawing. Boolean results use green for `true` and red for `false`, including their boxes and incoming arrows.
- Keep backgrounds plain: white in light mode and near-black in dark mode. Color outlines, important labels, and selected marks; large colored panels are usually unnecessary.
- Use the handwriting stack `Chalkboard`, `Comic Sans MS`, `cursive`, or an available legible handwritten font. Check the actual rendered font and text fit.
- Prefer simple nodes, arrows, grids, or tables. An introductory idea can be a few flat stages; it does not need a dependency tree. Use only the structure that helps explain this particular idea.
- Keep explanations in the surrounding prose. Inside the image, prefer names, values, and short state labels. Avoid infographic banners, decorative icons, gradients, shadows, polished cards, and large blocks of text.

## Draw the right thing

Read the supplied passage, example, or relevant source before choosing the composition. Preserve its names, values, and intended level of detail. For execution traces, preserve the observed call order and results. Distinguish call order from dependencies, and recomputation from a changed result.

Use the requested destination; otherwise choose an appropriate output location for the current task. Creating an illustration alone does not request edits to a blog post or repository.

Default to paired `name-light.svg` and `name-dark.svg` files unless the user requests one theme. Keep their geometry and wording identical.

## Reusable SVG helper

[scripts/sketch_svg.py](scripts/sketch_svg.py) provides `Sketch`, the palette, rough boxes and ellipses, text, paths, and matching colored arrowheads. Use Python 3.10+; no package dependencies are required. Use it for the repeated mechanics; author custom paths or plain SVG when the drawing benefits from them. The helper does not choose layouts or route connectors.

Import it from this skill's `scripts` directory in a task-local script:

```python
from pathlib import Path
from sketch_svg import Sketch

drawing = Sketch(900, 300, "An example", "Inputs pass through work to a result.")
drawing.box(40, 100, 200, 80, role="orange")
drawing.text(140, 150, "inputs", role="orange")
drawing.path("M 242 140 Q 300 135 358 140", role="blue", arrow=True)
drawing.box(360, 100, 200, 80, role="blue")
drawing.text(460, 150, "work", role="blue")
drawing.path("M 562 140 Q 620 135 678 140", role="green", arrow=True)
drawing.box(680, 100, 180, 80, role="green")
drawing.text(770, 150, "true", role="green")
drawing.save_pair(Path(output_directory) / "example")
```

Add this skill's `scripts` directory to the import path when needed. The helper's public methods have concise docstrings. `group()` and each method's `parent` argument support nested drawings and tables.

## Verify and deliver

Parse the SVG and render it with an existing renderer, such as Sharp or `rsvg-convert`. Discover installed tools or bundled runtime paths rather than relying on a particular machine's paths. Do not add a dependency just to draw the diagram.

Inspect both themes at the intended display size. Check label fit, contrast, connectors, arrowhead colors, and any clipped marks. If the labels become tiny, simplify or split the drawing instead of shrinking everything. Report only checks actually performed.

Deliver the SVG files with a PNG preview when available. Keep the reply brief.
