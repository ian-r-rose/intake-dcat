import argparse
import sys
import yaml

from intake.cli.bootstrap import main as run
from intake.cli.util import Subcommand

from .catalog import DCATCatalog
from .util import mirror_data


class Mirror(Subcommand):
    """
    Mirror a catalog subset specified in a manifest to a remote bucket.
    """

    name = "mirror"

    def initialize(self):
        self.parser.add_argument(
            "manifest",
            type=str,
            metavar="MANIFEST",
            help="Path to a manifest YAML file",
        )
        self.parser.add_argument(
            "--dry-run",
            help="If this flag is given, no upload occurs",
            action="store_true",
        )

    def invoke(self, args):
        upload = not args.dry_run
        catalog = mirror_data(args.manifest, upload=upload)
        print(yaml.dump(catalog))


class Create(Subcommand):
    """
    Create an intake YAML catalog from a DCAT catalog and print it to stdout.
    """

    name = "create"

    def initialize(self):
        self.parser.add_argument("uri", metavar="URI", type=str, help="Catalog URI")
        self.parser.add_argument(
            "--version", metavar="VERSION", type=str, help="Catalog version"
        )
        self.parser.add_argument(
            "--name", metavar="VERSION", type=str, help="Catalog name"
        )

    def invoke(self, args):
        version = args.version or None
        name = args.name or ""
        catalog = DCATCatalog(args.uri, name=name)
        new_catalog = {"metadata": {"name": name, "version": version}, "sources": {}}
        for key, entry in catalog.items():
            new_catalog["sources"][key] = yaml.safe_load(entry.yaml())["sources"][key]
        print(yaml.dump(new_catalog))


subcommands = [Mirror, Create]


def main(argv=None):
    return run("Intake DCAT CLI", subcommands, argv or sys.argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
