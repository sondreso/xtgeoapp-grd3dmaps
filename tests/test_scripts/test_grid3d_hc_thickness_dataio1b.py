"""Testing suite hc, using dataio output."""
import json
import os
import shutil
from pathlib import Path

import pytest
import xtgeo
import xtgeoapp_grd3dmaps.avghc.grid3d_hc_thickness as grid3d_hc_thickness
import yaml

YAMLCONTENT = """
title: Reek

# Using PORV as method, and a rotated template map in mapsettings
# Reproduce hc_thickness1g.yml

input:
  eclroot: tests/data/reek/REEK
  grid: tests/data/reek/reek_grid_fromegrid.roff
  dates:
    - 19991201

zonation:
  zranges:
    - Z1: [1, 5]

mapsettings:
  templatefile: tests/data/reek/reek_hcmap_rotated.gri

computesettings:
  # choose oil, gas or both
  mode: both                                  # <<
  critmode: No
  shc_interval: [0.1, 1] # saturation interv
  method: use_porv
  zone: Yes
  all: Yes
  unit: m   # e.g. 'feet'; if missing, default is 'm' for metric

output:
  tag: hcdataio1b
  mapfolder: fmu-dataio

"""
SOURCEPATH = Path(__file__).absolute().parent.parent.parent


def test_hc_thickness_1b_add2docs(datatree):
    """Test HC thickness map piped through dataio, using 'both' mode"""

    cfg = datatree / "hcdataio1b.yml"
    cfg.write_text(YAMLCONTENT)

    os.environ["FMU_GLOBAL_CONFIG"] = str(
        datatree / "tests" / "data" / "reek" / "global_variables.yml"
    )
    grid3d_hc_thickness.main(
        ["--config", "hcdataio1b.yml", "--dump", "dump_config.yml"]
    )

    # read result file
    res = datatree / "share" / "results" / "maps"
    surf = xtgeo.surface_from_file(res / "all--hcdataio1b_oilthickness--19991201.gri")
    assert surf.values.mean() == pytest.approx(1.09999, rel=0.01)

    # read metadatafile
    with open(
        res / ".all--hcdataio1b_oilthickness--19991201.gri.yml", encoding="utf8"
    ) as stream:
        metadata = yaml.safe_load(stream)

    if "DUMP" in os.environ:
        print(json.dumps(metadata, indent=4))

    assert metadata["data"]["spec"]["ncol"] == 161
    assert metadata["data"]["property"]["attribute"] == "oilthickness"

    # for auto documentation
    shutil.copy2(cfg, SOURCEPATH / "docs" / "test_to_docs")
