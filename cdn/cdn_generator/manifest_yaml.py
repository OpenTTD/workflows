import os
import pathlib

from cdn_generator.helpers import (
    list_folder,
    get_content,
    get_name,
)

# If this is part of the filename, these files are marked as "dev" files
DEV_IF_FILENAME_CONTAINS = [
    "docs",
    "source",
    "dbg.deb",
    "pdb.xz",
]


def _generate_manifest(category, folder, files, config):
    # Don't generate manifest.yaml if it already exists.
    if os.path.isfile(f"generated/{category}/{folder}/manifest.yaml"):
        return

    print(f"Creating manifest for {category} {folder} ...")

    name = get_name(folder, config)
    base_category = "-".join(category.split("-")[:-1])
    base = f"{base_category}-{folder}-"

    prefix = f"{category}/{folder}"
    manifest = []
    manifest_files = []
    manifest_dev_files = []

    changelog = None
    for id, size in files.items():
        if id.lower().startswith("changelog"):
            changelog = id

        if id.endswith((".html", ".md", ".txt", ".yaml", ".md5sum", ".sha1sum", ".sha256sum")):
            continue

        md5sum = get_content(f"{prefix}/{id}.md5sum").split(" ")[0]
        sha1sum = get_content(f"{prefix}/{id}.sha1sum").split(" ")[0]
        sha256sum = get_content(f"{prefix}/{id}.sha256sum").split(" ")[0]

        file_content = [
            f"- id: {id}",
            f"  size: {size}",
            f"  md5sum: {md5sum}",
            f"  sha1sum: {sha1sum}",
            f"  sha256sum: {sha256sum}",
        ]

        if not id.startswith(base):
            raise Exception(f"Filename '{id}' doesn't start with base '{base}'")

        if any([True for check in DEV_IF_FILENAME_CONTAINS if check in id]):
            manifest_dev_files.extend(file_content)
        else:
            manifest_files.extend(file_content)

    date = get_content(f"{prefix}/released.txt").replace(" ", "T").replace("TUTC", ":00-00:00")

    manifest.extend(
        [
            f"name: {name}",
            f"category: {base_category}",
            f"version: {folder}",
            f"date: {date}",
            f"base: {base}",
        ]
    )
    if changelog:
        manifest.append(f"changelog: {changelog}")
    manifest.append("files:")
    manifest.extend(manifest_files)
    manifest.append("dev_files:")
    manifest.extend(manifest_dev_files)

    pathlib.Path(f"generated/{category}/{folder}").mkdir(parents=True, exist_ok=True)
    with open(f"generated/{category}/{folder}/manifest.yaml", "w") as f:
        f.write("\n".join(manifest) + "\n")


def generate_manifests(category, config, filter_path=None):
    is_version_folder = config.get("sort") != "normal"

    # In case we expect subfolders, crawl into them before generating manifests
    if config.get("subfolders") is not None:
        _, folders = list_folder(category)
        # Make sure we don't recurse a second time
        old_subfolders = config["subfolders"]
        config["subfolders"] = None

        for folder in folders:
            skip_write = filter_path and not filter_path.startswith(f"{category}/{folder}/")
            if not skip_write:
                generate_manifests(f"{category}/{folder}", config, filter_path=filter_path)

        config["subfolders"] = old_subfolders
        return

    files, folders = list_folder(category, is_version_folder=is_version_folder)
    for folder in folders:
        skip_write = filter_path and not filter_path.startswith(f"{category}/{folder}/")

        if not skip_write:
            files, _ = list_folder(f"{category}/{folder}")
            _generate_manifest(category, folder, files, config)
