# Pipeline-generated LFS catalog experiment

This scenario submits a community bundle directly through a PR, without the CI
pipeline. The base branch contains a small basic template referencing a synthetic
fixture bundle image. The fixture's oversized CSV description survives OPM's
`bundle-object-to-csv-metadata` migration. The submitted bundle has a release
configuration that adds it to the same channel, replacing the fixture bundle.

The hosted and release pipelines render the template. The release pipeline must
create the catalog, add its LFS tracking rule, upload the object, and open a
catalog-update PR. Test setup does not create a catalog or track it with LFS.
The test checks the generated PR's pointer, then downloads the object in a fresh
checkout and verifies its size and SHA-256. It does not wait for the generated
catalog PR to complete its own hosted/release cycle or check the resulting index.

## Prepare the reusable fixture image

Generate outside the repository: the build context contains a 110 MB CSV. This
synthetic bundle is for catalog rendering only, not installation on a cluster.
The fixture is compressed in the image, but rendered data is genuinely oversized.

```bash
python3 local-dev/create-lfs-bundle-fixture.py /tmp/community-lfs-fixture
# Use a registry repository you can publish to and the pipeline can pull from.
export FIXTURE_IMAGE=quay.io/redhat-isv/YOUR_FIXTURE_REPOSITORY:lfs-fixture
podman build -t "$FIXTURE_IMAGE" /tmp/community-lfs-fixture
podman push --digestfile /tmp/community-lfs-fixture.digest "$FIXTURE_IMAGE"
```

Use the published digest rather than the tag for the test. The generator fixes
the fixture package to `test-e2e-community-lfs` and its version to `0.0.0`, matching
the scenario's base template and release configuration.

## Run manually

Use the normal integration-test prerequisites: stage cluster login, Ansible
vault password, and permissions to publish the pipeline test image. Choose a
fresh operator version, as with other community tests.

```bash
make build-and-test-community-fbc-lfs \
  OPERATOR_VERSION_RELEASE=YOUR_UNUSED_VERSION_RELEASE \
  INTEGRATION_TESTS_FBC_LFS_FIXTURE_IMAGE=quay.io/redhat-isv/YOUR_FIXTURE_REPOSITORY@sha256:YOUR_DIGEST
```

To reuse an already-built pipeline image, use
`make integration-test-community-fbc-lfs` with the same arguments and
`PIPELINE_IMAGE=...`. Neither legacy LFS boolean is needed. Namespaces use
`USER-comm-fbc-lfs-test-VERSION_RELEASE`, with no timestamp suffix.

## Local feasibility result

With OPM v1.71.0 (the pipeline image's version), a 303-byte basic template
referencing a locally built fixture image rendered a 118,250,563-byte catalog
using `--migrate-level bundle-object-to-csv-metadata`. `opm validate` accepted it.
That probe used package `lfs-probe`; the reusable generator uses the scenario's
package name and produced a 118,250,685-byte catalog, also accepted by
`opm validate`. The important assertion is output above the pipeline's
100,000,000-byte LFS tracking threshold. The probe catalog also passed a local
Git LFS round trip: pointer commit, object upload to a temporary bare repository,
and download in an independent checkout with matching size and SHA-256.

This confirms rendering feasibility, not a successful cluster integration run.
The community configuration, registry access and full pipeline execution must
still be verified by running the scenario manually.
