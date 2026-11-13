---
status: open
filed: 2026-11-11
area: synthetic-validation
---

# Is chapter 1 reinventing anything? An audit, and what it leaves to fix

Tony, 2026-11-11: *"review the dissertation chapter to ensure we are not reinventing anything."*
The chapter is `docs/dissertation/chapter-1-aim0.md` on `synth/dissertation-chapter-aim0` (pull
request #919, a draft); nothing here edits it. One Claude review agent read the chapter, the three
prior-art records and the round 1 and round 3 review records, and checked the chapter's scripts
against `main` by imports, function lists and docstrings.

⚠ **How far to trust this.** Nothing was run and no paper was opened. Every literature candidate
below is from the agent's memory and is a **candidate, not a finding**: it says where to look,
not what a source contains.

**The short answer.** The code reuse is mostly sound; three review rounds had already fixed the
worst of it. What is left is a few measurements on `main` the chapter neither cites nor
reconciles, and novelty wording for window sharing and the joint fit that rests on fields the
records list as unsearched.

## Against this repository

| in the chapter | already on `main` | to do |
|---|---|---|
| Real event rates and gaps measured through the 2 s merge: 9.7 and 22.0 events per hour; 1.7 % of fast gaps under 3 s | [`learned/runs/2026-10-08-stack-ceiling/README.md`](../learned/runs/2026-10-08-stack-ceiling/README.md) measures the same recordings in a 0.5 s window: 18.4 and 25.6 events per hour, about 4 % of gaps under 2 s | **Reconcile.** The chapter calls its shares lower bounds and does not cite the narrower measurement, so "rarely binds" in its separation section depends on a window the reader cannot see |
| Tools merge close pairs at (merge rule + ½) bins | `tools/measure_close_events.py`: a close-pair test on the detectors, same conclusion, by F1 | Cite it |
| One assembly holding every event: only the uniform null rejects | `tools/assembly_power.py` already measures that case (strength 1.0) | Cite it; the many-assembly axis is the chapter's own |
| `theory.load_gaps` reads `gaps.csv` itself | `bugarach.real_intervals.load_gaps` | Reuse |
| The general event-train form, implemented twice | `event_train.py` with `theory.fit_joint`, and `separation/real_intervals/intervals.py` | Keep one; mark the other superseded |
| Chance-cluster rate under unequal cell rates, by simulation | `tools/measure_chance_floor.py` has the closed form (`poisson_binomial_sf`) | Reuse; whether the two agree was not checked |
| Kreuz's indicator from F, derived only | `tools/synfire_scan.py` computes it through PySpike | Run it |
| Beyond-2-SE and sign-test logic in four scripts | each other | One function |
| Realistic event trains placed by patching the simulator's placement | `simulate_coordination(gap_source=, gap_mix=)` | Disclosed in the chapter; the general form is still untested on trains the supported route makes |

**Not a duplication, and worth one sentence in the chapter:** its pair, assembly and
latency-template generators exist because `bugarach.simulate` cannot plant any of the three.
That is the generator work the readiness route lists as owed
([`pipelines/stream-readiness.md`](../pipelines/stream-readiness.md)).

## Against the literature (candidates, not verified)

| the chapter's claim | where the same result may already exist | risk the claim is overstated |
|---|---|---|
| Window sharing g_n for Gaussian jitter is "new in form" | For two onsets, g₂ is the triangular-kernel integral of the pair-lag density: how count variance and count correlation depend on bin width. Look at the variance–time curve (Cox & Lewis 1966), bin-size dependence of spike-count correlation (Bair, Zohary & Koch 2001; Tetzlaff et al. 2008), and Feynman-Y against gate width in neutron noise analysis. For three onsets, the range of a normal sample (Tippett 1925; Hartley 1942). The repo's own record read Staude, Rotter & Grün 2008 as abstract only | **medium to high** for two onsets, medium for three |
| The joint fit across windows; new are the jittered-cluster forms | Feynman-alpha fits variance-to-mean across gate widths for a timescale; neutron multiplicity counting uses doubles and triples gate fractions | medium |
| The exact no-order mean of the order indicator, "not found" | Dominance-hierarchy statistics on sparse win–loss matrices (Landau's h; Appleby 1983; de Vries 1995) | medium: "not found" is fair, "new" would not be |
| The at-most-one-event term and the surrogate term | Dead-time corrections in photon counting (a hard core is a dead time); time-slide background estimation in gravitational-wave searches | low to medium; rests on three sources marked unopened |

**Records that disagree with the chapter**, none changing a number:
`synthetic_validation/prior_art/README.md` still lists the joint fit as new and Louis et al. 2010
as unopened; the folder README marks Coppersmith et al. and Shah & Wainwright as abstract only
while the chapter cites them unmarked for a negative claim; the chapter says no search was made
for the separation result while its own derivation cites the statistical-resolution literature.

## What to do, in order

1. Open Staude, Rotter & Grün 2008 and one Feynman-alpha source, then soften or keep "new in
   form" for two-onset window sharing. This is the one item that could change what the chapter
   claims. Papers come through Tony, one DOI at a time.
2. Reconcile the gap and rate numbers with the 0.5 s measurement. It also bears on the
   short-interval ruling
   ([todo](2026-10-08-the-stack-ceiling-and-the-short-interval-bench.md)).
3. The reuse items in the first table.
4. Bring the three records into agreement with the chapter.

None of this is on the route to the revised export
([ADR-0020](../adr/0020-one-route-from-a-folder-to-calls-per-stream.md)); item 2 is the only
one the route also needs.
