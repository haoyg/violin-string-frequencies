# Violin String Frequencies — A=415/440/441/442 Hz Reference Tables

Exact frequencies for the four violin strings (G3, D4, A4, E5) at the four reference pitches people actually use: A=415 (baroque), 440 (ISO standard), 441 and 442 Hz (common in European orchestras). It also covers fiddle cross tunings and cent deviations. All values are computed by a script, not typed by hand, and you can get them as JSON or CSV. If you just want to tune, the [free online violin tuner](https://violin-tuner.com/) uses the same numbers and supports all four reference pitches.

## Standard tuning (G–D–A–E), equal temperament

<!-- BEGIN standard -->
| String | Note | A=415 Hz | A=440 Hz | A=441 Hz | A=442 Hz |
|---|---:|---:|---:|---:|---:|
| IV | G3 | 184.86 | 196.00 | 196.44 | 196.89 |
| III | D4 | 276.98 | 293.66 | 294.33 | 295.00 |
| II | A4 | 415.00 | 440.00 | 441.00 | 442.00 |
| I | E5 | 621.80 | 659.26 | 660.75 | 662.25 |
<!-- END standard -->

At A=440 the strings are G3 196.00 / D4 293.66 / A4 440.00 / E5 659.26 Hz. Every other column is that column scaled by `A/440`. For example, A=442 multiplies everything by 442/440.

## Cent deviation from A=440

Changing the reference pitch shifts every string by the same number of cents:

<!-- BEGIN cents -->
| Reference | Ratio to 440 | Cents vs A=440 |
|---|---:|---:|
| A=415 Hz | 415/440 = 0.943182 | -101.27 |
| A=440 Hz | 440/440 = 1.000000 | +0.00 |
| A=441 Hz | 441/440 = 1.002273 | +3.93 |
| A=442 Hz | 442/440 = 1.004545 | +7.85 |
<!-- END cents -->

A=415 is roughly a semitone low (−101 cents), which is why baroque A sounds close to a modern A♭.

## Equal temperament vs. pure fifths

Most violinists tune the A string to the reference and then tune the other strings by ear in pure 3:2 fifths, not equal-tempered fifths. Each pure fifth is about 1.96 cents wider than the equal-tempered one, so the G and E strings land a little further from A:

<!-- BEGIN pure -->
| Note | Equal (A=440) | Pure fifths (A=440) | Pure − equal (cents) | Equal (A=442) | Pure fifths (A=442) |
|---|---:|---:|---:|---:|---:|
| G3 | 196.00 | 195.56 | -3.91 | 196.89 | 196.44 |
| D4 | 293.66 | 293.33 | -1.96 | 295.00 | 294.67 |
| A4 | 440.00 | 440.00 | +0.00 | 442.00 | 442.00 |
| E5 | 659.26 | 660.00 | +1.96 | 662.25 | 663.00 |
<!-- END pure -->

Electronic tuners almost always show equal temperament. The JSON includes both values for every string.

## Cross tunings (scordatura)

Strings listed from low (IV) to high (I), equal temperament:

<!-- BEGIN cross -->
| Tuning | A (Hz) | IV | III | II | I |
|---|---:|---:|---:|---:|---:|
| AEAE | 440 | A3 220.00 | E4 329.63 | A4 440.00 | E5 659.26 |
| AEAE | 442 | A3 221.00 | E4 331.13 | A4 442.00 | E5 662.25 |
| GDGD | 440 | G3 196.00 | D4 293.66 | G4 392.00 | D5 587.33 |
| GDGD | 442 | G3 196.89 | D4 295.00 | G4 393.78 | D5 590.00 |
| ADAD | 440 | A3 220.00 | D4 293.66 | A4 440.00 | D5 587.33 |
| ADAD | 442 | A3 221.00 | D4 295.00 | A4 442.00 | D5 590.00 |
| ADAE | 440 | A3 220.00 | D4 293.66 | A4 440.00 | E5 659.26 |
| ADAE | 442 | A3 221.00 | D4 295.00 | A4 442.00 | E5 662.25 |
| GDAD | 440 | G3 196.00 | D4 293.66 | A4 440.00 | D5 587.33 |
| GDAD | 442 | G3 196.89 | D4 295.00 | A4 442.00 | D5 590.00 |
<!-- END cross -->

Values for A=415 and A=441 are in [`data/cross-tunings.csv`](data/cross-tunings.csv) and the JSON.

## Data files

| File | Contents |
|---|---|
| [`data/violin-frequencies.json`](data/violin-frequencies.json) | Everything: standard tuning, pure fifths, cents, cross tunings |
| [`data/standard-gdae.csv`](data/standard-gdae.csv) | GDAE at each reference pitch, equal + pure fifths |
| [`data/cross-tunings.csv`](data/cross-tunings.csv) | Every cross tuning at each reference pitch |

### Using the JSON

```js
const url = "https://raw.githubusercontent.com/haoyg/violin-string-frequencies/main/data/violin-frequencies.json";
const data = await (await fetch(url)).json();

data.standard_gdae["442"].map(s => `${s.note}: ${s.equal_hz} Hz`);
// ["G3: 196.89 Hz", "D4: 295 Hz", "A4: 442 Hz", "E5: 662.25 Hz"]

data.cross_tunings.AEAE["440"].map(s => s.equal_hz);
// [220, 329.63, 440, 659.26]
```

```python
import json, urllib.request
url = "https://raw.githubusercontent.com/haoyg/violin-string-frequencies/main/data/violin-frequencies.json"
data = json.load(urllib.request.urlopen(url))
for s in data["standard_gdae"]["415"]:
    print(s["note"], s["equal_hz"], s["pure_fifths_hz"])
```

Each string entry has `string` (IV–I), `note`, `equal_hz`, and, in standard tuning, also `pure_fifths_hz`, `pure_vs_equal_cents` and `cents_vs_a440`. Frequencies are rounded to 2 decimals. If you need more precision, run the script with `DECIMALS` raised.

## Source and verification

All numbers come from [`scripts/generate.py`](scripts/generate.py) (Python 3, standard library only):

- **Equal temperament:** `f = A × 2^(n/12)`, where `n` is the number of semitones from A4 (G3 = −14, D4 = −7, E5 = +7).
- **Pure fifths:** `D4 = A × 2/3`, `G3 = A × 4/9`, `E5 = A × 3/2`.
- **Cents:** `1200 × log2(f / f_ref)`.

To reproduce or check the data:

```sh
python3 scripts/generate.py           # regenerates data/ and the tables in this README
python3 scripts/generate.py --check   # exits non-zero if anything is out of date
```

The tables in this README sit between `<!-- BEGIN … -->` markers and are rewritten by the script, so the README and the data files can't drift apart. If you find a value that seems wrong, please open an issue and include the formula you used.

## License

[MIT](LICENSE). Use the data in apps, tuners, papers or teaching material. Attribution is appreciated but not required.
