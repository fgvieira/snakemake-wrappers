__author__ = "Filipe G. Vieira"
__copyright__ = "Copyright 2024, Filipe G. Vieira"
__license__ = "MIT"

import os
import tempfile
from snakemake.shell import shell

extra = snakemake.params.get("extra", "")
log = snakemake.log_fmt_shell(stdout=True, stderr=True)


# Input
if snakemake.input.get("tax_map"):
    extra += f" --tax-mapping-file {snakemake.input.tax_map}"
taxdump = snakemake.input.get("taxdump")


# TODO: arbitrary output file names
out = snakemake.output
if isinstance(out, list):
    out = os.path.commonprefix(out).rstrip("_")


with tempfile.TemporaryDirectory() as tmpdir:
    # Modules with threads
    if snakemake.params.module in ["databases"]:
        input = ""
        extra = f"--threads {snakemake.threads} {extra}"
    # Modules with no temp folder
    if snakemake.params.module in ["createdb"]:
        input = snakemake.input.fas
        tmpdir = ""
    # Modules with no out folder
    if snakemake.params.module in ["createtaxdb"]:
        input = snakemake.input.db
        out = ""
    # Auto-uncompress taxdump file
    if taxdump:
        if taxdump.endswith(".tar.gz"):
            import tarfile

            tar = tarfile.open(taxdump, "r:gz")
            taxdump = tmpdir / "taxdump"
            tar.extractall(taxdump)
            tar.close()
        extra += f" --ncbi-tax-dump {taxdump}"

    shell("mmseqs {snakemake.params.module} {input} {out} {tmpdir} {extra} {log}")
