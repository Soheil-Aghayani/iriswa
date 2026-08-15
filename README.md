<div align="center">
  <img src="docs/readme-hero.svg" alt="IRISWA visual hero" width="100%">

  <h1>IRISWA · انجمن مدیریت پسماند ایران</h1>
  <p><strong>A Persian publishing system for environmental knowledge, events, courses, and solid-waste practice.</strong></p>
  <p>
    <a href="https://soheil-aghayani.github.io/iriswa/"><strong>Open the live website →</strong></a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Persian_RTL-publishing-0B2F36?style=for-the-badge" alt="Persian RTL publishing">
    <img src="https://img.shields.io/badge/static_site-generated-1D6B70?style=for-the-badge" alt="Generated static site">
    <img src="https://img.shields.io/badge/environmental_knowledge-E5A24B?style=for-the-badge&labelColor=0B2F36" alt="Environmental knowledge">
  </p>
</div>

---

## What this repo does

IRISWA combines a Persian environmental website with a small content pipeline. Markdown content, reusable layout sections, and a Python builder produce the public HTML pages for news, courses, conferences, publications, waste law, and member-facing information.

## Public sections

- Association overview, board, branches, committees, and contact
- Environmental news and emergency HSE sessions
- Waste-management law and technology explainers
- Courses, conferences, sessions, and publications
- Search and a local content-generation workflow

## Build the site

~~~bash
git clone https://github.com/Soheil-Aghayani/iriswa.git
cd iriswa
python -m pip install markdown
python build.py
~~~

The builder writes the generated pages into the repository root so they can be served directly by GitHub Pages.

~~~bash
python -m http.server 8080
~~~

Open http://localhost:8080.

## Content workflow

1. Update the Markdown source or reusable section.
2. Run python build.py.
3. Review the generated page and links locally.
4. Commit the generated output together with the source change.

> The static admin page is a convenience tool for generating Markdown. It is not a production authentication boundary and should not be used to protect private content.

<div align="center">
  <sub>Environmental information, published clearly and built to be maintained.</sub>
</div>
