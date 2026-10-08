# Figure deck and artwork regeneration

`FIGURE_DECK.pptx` is a submission-support deck with editable slide titles,
captions, and provenance notes. The figure artwork on each slide is a placed
PNG and is not editable as separate axes, series, or labels in PowerPoint.

The authoritative editable sources are the repository result tables and
`scripts/build_outputs.py`. From the project root, regenerate every PNG, PDF,
and SVG figure with:

```bash
make figures
```

After changing figure code or source results, rerun `make package` to rebuild
the deck and submission archive. This distinction prevents image-based slides
from being represented as element-editable charts.
