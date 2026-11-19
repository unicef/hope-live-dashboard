# Icon sources

The public pages use a small Lucide icon subset on the standard 24×24 grid
(`stroke-width="2"`, round caps and joins, `currentColor`).

- Source: Lucide Static 1.72.0
- Licence: ISC, see `LICENSE`
- Do not add width/height to the root `<svg>`; sizing comes from CSS classes.

## Add or update an icon

1. Drop the kebab-case SVG into this folder.
2. Run:

   ```bash
   python src/hope_live/theme/icons/build_icons.py
   ```

3. Commit the source SVG plus the two generated files:

   - `src/hope_live/templates/includes/icons_sprite.html`
   - `src/hope_live/templatetags/icon_names.py`

## Use an icon

```django
{% load icons %}
{% icon "children" "h-4 w-4" %}
```

The sprite is included once by `public_layout.html`. Icons are `aria-hidden`
because they sit next to text. Icon-only buttons must have an `aria-label` on
the button itself.
