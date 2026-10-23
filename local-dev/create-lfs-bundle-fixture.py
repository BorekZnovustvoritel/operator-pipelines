"""Generate a synthetic bundle image build context for the LFS integration test.

The oversized description survives OPM's CSV metadata migration. This bundle is
catalog test data, not an operator intended to be installed on a cluster.
"""

import argparse
import json
from pathlib import Path


def main() -> None:
    """Write a build context without building or publishing an image."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    manifests = args.output / "manifests"
    metadata = args.output / "metadata"
    manifests.mkdir()
    metadata.mkdir()
    package = "test-e2e-community-lfs"
    annotations = {
        "operators.operatorframework.io.bundle.mediatype.v1": "registry+v1",
        "operators.operatorframework.io.bundle.manifests.v1": "manifests/",
        "operators.operatorframework.io.bundle.metadata.v1": "metadata/",
        "operators.operatorframework.io.bundle.package.v1": package,
        "operators.operatorframework.io.bundle.channels.v1": "stable",
    }
    (metadata / "annotations.yaml").write_text(
        json.dumps({"annotations": annotations}), encoding="utf-8"
    )
    csv = {
        "apiVersion": "operators.coreos.com/v1alpha1",
        "kind": "ClusterServiceVersion",
        "metadata": {"name": f"{package}.v0.0.0"},
        "spec": {
            "displayName": "Synthetic LFS catalog fixture",
            "description": "LFS render fixture. " * 5_500_000,
            "version": "0.0.0",
            "install": {"strategy": "deployment", "spec": {"deployments": []}},
        },
    }
    (manifests / "csv.yaml").write_text(json.dumps(csv), encoding="utf-8")
    dockerfile = "FROM scratch\n"
    dockerfile += "".join(
        f"LABEL {key}={json.dumps(value)}\n" for key, value in annotations.items()
    )
    dockerfile += "COPY manifests /manifests/\nCOPY metadata /metadata/\n"
    (args.output / "Dockerfile").write_text(dockerfile, encoding="utf-8")
    print(f"Created synthetic fixture build context: {args.output}")


if __name__ == "__main__":
    main()
