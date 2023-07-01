import boto3
import os
import sys

from botocore.exceptions import ClientError

from cdn_generator.version_sort import version_sort

BUCKET = None

client = boto3.client("s3", endpoint_url=os.getenv("S3_ENDPOINT_URL"))


class UnknownOverrideName(Exception):
    pass


def list_folder(prefix, is_version_folder=False):
    if not prefix.endswith("/"):
        prefix += "/"
    if prefix == "/":
        prefix = ""

    files = {}
    folders = []

    listing = {
        "IsTruncated": True,
    }
    while listing["IsTruncated"]:
        kwargs = {}
        if "NextContinuationToken" in listing:
            kwargs["ContinuationToken"] = listing["NextContinuationToken"]

        listing = client.list_objects_v2(
            Bucket=BUCKET,
            Delimiter="/",
            Prefix=prefix,
            **kwargs,
        )

        if "Contents" in listing:
            files.update({obj["Key"][len(prefix) :]: obj["Size"] for obj in listing["Contents"]})

        if "CommonPrefixes" in listing:
            folders.extend([obj["Prefix"][len(prefix) : -1] for obj in listing["CommonPrefixes"]])

    files = {f: files[f] for f in sorted(files.keys(), key=lambda s: s.lower())}
    if is_version_folder:
        folders.sort(key=version_sort)
    else:
        folders.sort()

    return files, folders


def get_content(key):
    try:
        content = client.get_object(
            Bucket=BUCKET,
            Key=key,
        )
    except ClientError:
        print(f"Tried getting object '{key}'", file=sys.stderr)
        raise
    return content["Body"].read().decode().strip()


def delete_files(files):
    client.delete_objects(
        Bucket=BUCKET,
        Delete={
            "Objects": [{"Key": file} for file in files],
            "Quiet": True,
        },
    )


def get_name(folder, config):
    override_name = config.get("override-name")
    if override_name is None:
        # If there is a "-" in the version (which is the folder), it is a
        # testimg release. Examples: 1.2.3-beta1, 1.2.3-RC2.
        if "-" in folder:
            name = "testing"
        else:
            name = "stable"
    elif override_name == "in-folder-name":
        # These binaries are in the form of YYYYMMDD-NAME-...
        name = folder.split("-")[1]
    elif override_name == "nightly":
        name = "nightly"
    else:
        raise UnknownOverrideName(f"Unknown override-name value '{override_name}' for {folder}")

    return name


def set_bucket_id(bucket_id):
    global BUCKET
    BUCKET = bucket_id
