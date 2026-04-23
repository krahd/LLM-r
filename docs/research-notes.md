# Research Notes (April 23, 2026)

This implementation is based on current docs and community standards for Live automation.

## Key findings

1. **Best bridge pattern today:** Use a Live Remote Script for robust in-DAW control, then connect from external app over OSC.
2. **AbletonOSC** is a practical option because it already maps many Live operations into OSC endpoints.
3. **Safety reality:** Live APIs expose control and arrangement/session operations but not unrestricted raw audio DSP editing from external code in the same way as a full offline DAW render pipeline.

## Primary sources

- Ableton Help Center — Controlling Live using Max for Live: https://help.ableton.com/hc/en-us/articles/5402681764242-Controlling-Live-using-Max-for-Live
- Ableton Help Center — Installing third-party remote scripts: https://help.ableton.com/hc/en-us/articles/209072009-Installing-third-party-remote-scripts
- AbletonOSC repository: https://github.com/ideoforms/AbletonOSC
- AbletonOSC paper (Zenodo DOI): https://zenodo.org/doi/10.5281/zenodo.11189234

