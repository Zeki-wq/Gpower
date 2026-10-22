# AP_04 — GUI oracle record

- Reference application: G*Power 3.1.9.4 (live Windows GUI)
- Test: t tests → Means: Difference between two independent means (two groups)
- Analysis: A priori; tails = Two (two-tailed)
- Inputs: d = 0.5; α = 0.05; target power = 0.8; allocation ratio N2/N1 = 1
- G*Power GUI outputs: N1=64, N2=64, total N=128, df=126, δ=2.8284271, critical t=1.9789706, actual power=0.8014596
- Fresh clone run: yes, through src.calculator in the project’s isolated Python 3.12 virtual environment. Outputs: N1=64, N2=64, total N=128, df=126, δ=2.828427, critical t=1.978971, actual power=0.801460
- Comparison: MATCH — N1, N2, and df match exactly; numerical outputs are within 1e-4.
- Evidence: screenshots/gui_pilot_001.png (real G*Power window capture)
