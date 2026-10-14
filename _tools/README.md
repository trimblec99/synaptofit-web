# _tools

`build_legal_html.py` is the source of truth for the four pages in /legal.

**Never hand-edit the HTML in /legal.** Edit this script and re-run it:

    python _tools\build_legal_html.py

It detects the repo layout and writes straight into /legal. Then commit and push.

Constants at the top: VERSION, UPDATED, TRADER, ADDR_1L, ADDR_BL, BASE.
Bump VERSION only for a material change - it drives the in-app re-consent check.
