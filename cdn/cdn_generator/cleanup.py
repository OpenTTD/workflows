import datetime
import dateutil.relativedelta
import os

from cdn_generator.helpers import delete_files, list_folder
from cdn_generator.manifest_yaml import _generate_manifest
from cdn_generator.directory_listing import _generate_directory_listing_single


def _cleanup_directory(folder, keep_source, do_delete):
    files, folders = list_folder(folder)
    if len(folders) != 0:
        raise Exception(f"Unexpected folders while cleaning up in {folder}")

    deleting = []
    for file in files:
        if keep_source:
            # Keep the source package.
            if "-source.tar.xz" in file:
                continue
            # As this folder won't be empty, keep the files that indicate what this folder is about too.
            if file in (
                "index.html",
                "manifest.yaml",
                "README.md",
                "readme.txt",
                "README.txt",
                "released.txt",
            ):
                continue
            if file.lower().startswith("changelog"):
                continue

        fullname = f"{folder}/{file}"
        deleting.append(fullname)

    if not deleting:
        return deleting

    if do_delete:
        print(f"Deleting {folder} ...")
        delete_files(deleting)
    else:
        print(f"Collecting what to delete for {folder} ...")

    return deleting


def cleanup_category(category, config, filter_path=None, do_delete=False):
    after = config["cleanup-after"]
    if after.endswith("mo"):
        after = dateutil.relativedelta.relativedelta(months=int(after[:-2]))
    elif after.endswith("d"):
        after = dateutil.relativedelta.relativedelta(days=int(after[:-1]))

    cutoff_date = datetime.datetime.today() - after
    cutoff_date = f"{cutoff_date.year}{cutoff_date.month:02d}{cutoff_date.day:02d}"

    deleting = []

    if config.get("subfolders") is not None:
        _, folders = list_folder(category)
        # Make sure we don't recurse a second time
        old_subfolders = config["subfolders"]
        config["subfolders"] = None

        for folder in folders:
            skip_write = filter_path and not filter_path.startswith(f"{category}/{folder}/")
            if not skip_write:
                deleting.extend(cleanup_category(f"{category}/{folder}", config, filter_path, do_delete))

        config["subfolders"] = old_subfolders
        return deleting

    _, folders = list_folder(category)
    folders = sorted(folders)

    keep = config["cleanup-keep"]
    keep_source = False
    if keep == "source":
        keep = 0
        keep_source = True
    else:
        folders = folders[:-keep]

    last_run_date = os.getenv("CLEANUP_LAST_RUN_DATE")

    for folder in folders:
        date = folder.split("-")[0]

        # Skip anything before this date, as it is already considered done.
        if last_run_date and date < last_run_date:
            continue

        if date < cutoff_date:
            deleting_item = _cleanup_directory(f"{category}/{folder}", keep_source, do_delete)
            deleting.extend(deleting_item)

            if do_delete and deleting_item and keep_source:
                files, _ = list_folder(f"{category}/{folder}")
                _generate_manifest(category, folder, files, config)
                _generate_directory_listing_single(f"{category}/{folder}", False)

    return deleting
