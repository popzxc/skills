---
name: zola-add-image
description: "Add supplied images to a Zola blog post, organizing post-specific assets and following the site's light/dark theme. Use when explicitly invoked."
---

# Zola Add Image

Add the requested image at the requested place in an existing Zola post. Limit edits to the image assets and the requested insertion or replacement; preserve the author's prose, code examples, frontmatter, and draft status.

## Find the post and its conventions

Use the project already identified in the request or conversation. Inspect its instructions, `zola.toml` or `config.toml`, blog content, page template, and image/theme styles. Resolve the unfinished post from that context. Ask only if the project, post, or quoted insertion point remains ambiguous.

Common layout:

```text
content/blog/<date>-<slug>.md
static/assets/<date>-<slug>/
templates/page.html
static/site.css
```

Follow an existing post asset folder or page-bundle convention. Otherwise create `static/assets/<post-filename-without-extension>/` and use descriptive filenames. Copy supplied images without redrawing or recoloring them. Use matching `name-light.svg` and `name-dark.svg` names when variants are provided.

Zola copies `static/` into the output root: `static/assets/...` becomes `/assets/...`, not `/static/assets/...`. Check `base_url` for a deployment path prefix and follow the project's URL convention when one is present. Ordinary Markdown does not evaluate arbitrary Tera template expressions; reuse an existing URL shortcode if the site needs one.

## Insert the image

When the user quotes part of a paragraph, insert after the complete matching paragraph unless they specify otherwise. Preserve everything outside the requested insertion or replacement. Reread the post immediately before editing so concurrent changes are not overwritten.

Use the site's existing source of theme state. For a site following `prefers-color-scheme`, use a native `picture` element with a light fallback:

```html
<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="/assets/<post>/concept-dark.svg" type="image/svg+xml">
    <img src="/assets/<post>/concept-light.svg" alt="A concise description of the illustration." width="1280" height="520" loading="lazy" decoding="async">
  </picture>
</p>
```

Replace the example path, alt text, and dimensions with the actual image's values. The paragraph wrapper provides normal article spacing without changing the page template. Existing prose styles commonly already set `max-width: 100%` and `height: auto` on images; inspect them before adding CSS.

A manually selected theme can override the operating-system preference. In that case, follow the site's existing theme selector and image pattern; a media-only `picture` will not follow a manual override. Keep the site's theme system intact.

For a single image, use the project's ordinary image markup. Do not invent or invert a second variant merely to have two files. Keep source diagrams as SVG when supplied. Use meaningful alt text; for a trace or table, include the essential result rather than repeating a vague title.

## Verify and finish

Run the project's normal checks. For local asset work, these are useful defaults:

```sh
zola check --drafts --skip-external-links
zola build --drafts --output-dir <task-owned-temporary-directory>
```

Use a fresh temporary build directory so the user's existing preview is preserved. Check the generated post and copied assets. When browser verification is available, trigger lazy image loading, confirm the selected image's `currentSrc` in both themes, and inspect sizing and legibility at the article width and a narrow viewport. Do not claim browser checks if only the generated HTML was inspected.

Leave the local changes ready for review. Publishing, staging, committing, or opening a pull request is separate work and is not implied by adding an image. Finish with a brief link to the updated post and any relevant verification result.
