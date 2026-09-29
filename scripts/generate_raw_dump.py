"""Generate data/raw/maude_dump.jsonl: a synthetic, deliberately messy MAUDE-like file.

Nothing in the app reads this file. It exists so course exercises have a big,
noisy dataset to explore. Run from the project root:

    python scripts/generate_raw_dump.py
"""

import json
import random
from datetime import date, timedelta
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "data" / "raw" / "maude_dump.jsonl"
TARGET_BYTES = 4_000_000
SEED = 2024

DEVICES = [  # (brand name, generic name, manufacturer)
    ("Azure XT DR MRI", "Pacemaker, implantable", "Medtronic"),
    ("Assurity MRI", "Pacemaker, implantable", "Abbott"),
    ("Cobalt XT DR", "Implantable cardioverter defibrillator", "Medtronic"),
    ("EMBLEM S-ICD", "Implantable cardioverter defibrillator, subcutaneous", "Boston Scientific"),
    ("TactiFlex SE", "Catheter, ablation, cardiac", "Abbott"),
    ("THERMOCOOL SMARTTOUCH SF", "Catheter, ablation, cardiac", "Biosense Webster"),
    ("da Vinci Xi", "System, surgical, computer controlled instrument", "Intuitive Surgical"),
    ("Hugo RAS", "System, surgical, computer controlled instrument", "Medtronic"),
]
EVENT_TYPES = ["Malfunction"] * 5 + ["Injury"] * 3 + ["Death", "No answer provided"]
PROBLEMS = [
    "battery depletion", "lead fracture", "loss of capture", "inappropriate shock", "oversensing",
    "device stopped functioning", "unintended movement", "steam pop during ablation", "software error",
]
OPENINGS = [
    "It was reported that the device experienced {problem} during {setting}.",
    "The customer reported {problem}. The patient was {patient}.",
    "A field representative reported {problem} for a device implanted in (b)(6) {year}.",
]
MIDDLES = [
    "The device was explanted and returned for analysis.",
    "The device was not returned to the manufacturer; analysis could not be performed.",
    "Interrogation showed the event counter had incremented (b)(4).",
    "No patient harm was reported at the time of the event.",
    "The patient was hospitalized for observation and discharged the following day.",
]
ENDINGS = [
    "Investigation is ongoing and a supplemental report will follow.",
    "Analysis confirmed the reported failure mode; the root cause is (b)(4).",
    "This report is being submitted based on the information available at this time.",
]
SETTINGS = ["follow-up", "implant", "a routine check", "the procedure", "an emergency visit"]
PATIENTS = ["asymptomatic", "symptomatic", "stable", "transferred to the ICU"]


def messy(text: str, rng: random.Random) -> str:
    """Add the kind of noise real free-text fields have: casing, spaces, typos."""
    roll = rng.random()
    if roll < 0.15:
        text = text.upper()
    elif roll < 0.25:
        text = text.lower()
    if rng.random() < 0.3:
        text = text.replace(" ", "  ", rng.randint(1, 3))
    if rng.random() < 0.2:
        pos = rng.randrange(len(text))
        text = text[:pos] + text[pos + 1:]
    return text


def make_report(index: int, rng: random.Random) -> dict:
    """Build one MAUDE-like report as a dict; some fields are randomly missing."""
    brand, generic, manufacturer = rng.choice(DEVICES)
    received = date(2019, 1, 1) + timedelta(days=rng.randint(0, 2400))
    problem = rng.choice(PROBLEMS)
    opening = rng.choice(OPENINGS).format(
        problem=problem, setting=rng.choice(SETTINGS),
        patient=rng.choice(PATIENTS), year=received.year - rng.randint(0, 6),
    )
    sentences = [opening, *rng.sample(MIDDLES, rng.randint(1, 3)), rng.choice(ENDINGS)]
    report = {
        "mdr_report_key": str(10_000_000 + index),
        "report_number": f"{rng.randint(1_000_000, 9_999_999)}-{received.year}-{rng.randint(1, 99999):05d}",
        "date_received": received.strftime(rng.choice(["%Y%m%d", "%Y-%m-%d", "%m/%d/%Y"])),
        "event_type": rng.choice(EVENT_TYPES),
        "brand_name": messy(brand, rng),
        "generic_name": generic,
        "manufacturer": messy(manufacturer, rng),
        "product_problem": problem.capitalize(),
        "narrative": messy(" ".join(sentences), rng),
    }
    for field in ("product_problem", "manufacturer", "event_type"):
        if rng.random() < 0.05:
            report.pop(field)
    return report


def main() -> None:
    """Write JSONL until the file reaches TARGET_BYTES (about 4 MB)."""
    rng = random.Random(SEED)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    written, index = 0, 0
    with OUTPUT.open("w", encoding="utf-8") as handle:
        while written < TARGET_BYTES:
            line = json.dumps(make_report(index, rng)) + "\n"
            repeats = 2 if rng.random() < 0.02 else 1  # a few duplicates, like the real thing
            handle.write(line * repeats)
            written += len(line.encode("utf-8")) * repeats
            index += 1
    print(f"Wrote {index} reports ({written / 1_000_000:.1f} MB) to {OUTPUT}")


if __name__ == "__main__":
    main()
