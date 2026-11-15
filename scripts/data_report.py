from sfp.config import load_instruments
from sfp.quality import quality_report

print(quality_report(load_instruments()).to_string())
