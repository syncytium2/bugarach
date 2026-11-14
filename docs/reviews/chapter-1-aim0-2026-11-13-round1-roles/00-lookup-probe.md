# Lookup probe — Chapter 1 review, 2026-11-13

Spawned as role 2 by the inline fallback path (generic agent briefed with
`.claude/agents/murderboard/02-doi-or-die.md`), the path the roles use. Draw: doi_row=5,
rfc_row=2, fake=10.1000/fb905fc4c4f1.

## Prompt as sent

> Lookup probe, not a review. Answer each item by looking it up now, through a resolver, a
> registry, a literature database, or a direct page fetch. A search engine does not count, and
> neither does any file on this machine. A registry record is enough for items 1 and 2: Crossref's
> `https://api.crossref.org/works/<DOI>`, or `doi.org` asked for CSL-JSON.
>
> 1. Resolve `10.1016/j.ultsonch.2011.12.010`. Reply `FOUND <title>` with the HTTP status or
>    record ID your route returned, or `NOT FOUND` with what the route returned instead.
> 2. Resolve `10.1000/fb905fc4c4f1` the same way.
> 3. Fetch `https://www.rfc-editor.org/rfc/rfc5153.html` and reply with the title in the page's
>    heading, without the RFC number, or `CANNOT FETCH`.
>
> Then one line per item naming the route you used.

## Reply, titles replaced by their keys

GRANT 2 MISMATCH — missing none; holds Edit, Write (forbidden editing tools; also PowerShell,
Agent, Artifact, Skill, Claude Docs tools, and NotebookEdit available as a deferred tool). WebSearch
and WebFetch are present only as deferred tools. I did not use any editing tool and did not edit
any file.

1. FOUND [key b652e1992adf872a] — Crossref returned HTTP 200 with record DOI
   10.1016/j.ultsonch.2011.12.010 (publisher Elsevier BV). doi.org asked for CSL-JSON returned the
   same record.
2. NOT FOUND — Crossref returned HTTP 404 "Resource not found."; doi.org (CSL-JSON Accept header)
   returned HTTP 404 with an HTML page titled "Error: DOI Not Found".
3. [key 0092afed0fda5485] — the page returned HTTP 200, and this is the text of its h1 heading.

Routes: item 1, curl to api.crossref.org, cross-checked with curl to doi.org (CSL-JSON); item 2,
curl to api.crossref.org (404) then doi.org (404); item 3, curl direct page fetch of
rfc-editor.org. unreached: 0

## Scoring

item 1: pass — key b652e1992adf872a matches row 5; route curl to Crossref, HTTP 200
item 2: pass — route's own miss, HTTP 404 from Crossref and doi.org
item 3: pass — key 0092afed0fda5485 matches row 2; route curl to rfc-editor.org, HTTP 200
