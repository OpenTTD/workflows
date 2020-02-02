import os
import pathlib

from cdn_generator.helpers import list_folder


def _generate_folders_yaml(prefix, folders):
    if not folders:
        return

    folders_content = [
        "folders:",
    ]
    for folder in folders:
        folders_content.append(f"- name: {folder}")

    pathlib.Path(f"generated/{prefix}").mkdir(parents=True, exist_ok=True)
    with open(f"generated/{prefix}/folders.yaml", "w") as f:
        f.write("\n".join(folders_content) + "\n")


def _generate_index_html(prefix, folders, files):
    html_content = [
        "<html>",
        f"<head><title>Index of /{prefix}</title></head>",
        '<body bgcolor="white">',
        f"<h1>Index of /{prefix}</h1>",
        "<hr>",
        "<pre>",
    ]

    if prefix != "/":
        html_content.append('<a href="../">../</a>')

    for folder in folders:
        html_content.append(f'<a href="{folder}/">{folder}/</a>')

    for id, size in files.items():
        # These sums are already in manifest.yaml; there is no need to link to
        # them directly, as it makes the index file hard to read.
        if id.endswith((".md5sum", "sha1sum", "sha256sum")):
            continue

        # Align with spaces; this is done by most httpds too
        size = " " * (70 - len(id)) + str(size)
        html_content.append(f'<a href="{id}">{id}</a> {size}')

    html_content.extend(["</pre>", "<hr>", "</body>", "</html>"])

    pathlib.Path(f"generated/{prefix}").mkdir(parents=True, exist_ok=True)
    with open(f"generated/{prefix}/index.html", "w") as f:
        f.write("\n".join(html_content) + "\n")


def _generate_directory_listing(prefix, files, folders):
    print(f"Creating directory listing for {prefix} ...")

    # Generate a folders.yaml and latest.yaml
    _generate_folders_yaml(prefix, folders)

    # It is possible we rendered some files locally; add these to the list too.
    for f in os.listdir(f"generated/{prefix}"):
        if os.path.isfile(f"generated/{prefix}/{f}"):
            files[f] = os.stat(f"generated/{prefix}/{f}").st_size
    # Hide existing index.html from the index
    if "index.html" in files:
        del files["index.html"]

    _generate_index_html(prefix, folders, files)


def _generate_directory_listing_single(prefix, is_version_folder, filter_path=None):
    files, folders = list_folder(prefix, is_version_folder=is_version_folder)

    # Reverse the folders to make sure the latest version is on top (sorting
    # is already done by list_folder()).
    folders.reverse()
    _generate_directory_listing(prefix, files, folders)

    for folder in folders:
        skip_write = filter_path and not filter_path.startswith(f"{prefix}/{folder}/")

        if not skip_write:
            files, folders = list_folder(f"{prefix}/{folder}")
            _generate_directory_listing(f"{prefix}/{folder}", files, folders)


def generate_directory_listing(category, config, filter_path=None):
    is_version_folder = config.get("sort") != "normal"

    if config.get("subfolders") is None:
        _generate_directory_listing_single(category, is_version_folder, filter_path=filter_path)
        return

    files, folders = list_folder(category)
    _generate_directory_listing(category, files, folders)

    for folder in folders:
        skip_write = filter_path and not filter_path.startswith(f"{category}/{folder}/")

        if not skip_write:
            _generate_directory_listing_single(f"{category}/{folder}", is_version_folder, filter_path=filter_path)


def generate_directory_listing_root(category, ignore_folders):
    files, folders = list_folder(category)

    # Remove the folders we ignore (this is only supported on root-level)
    if ignore_folders is not None:
        for folder in ignore_folders:
            if folder in folders:
                folders.remove(folder)

    _generate_directory_listing(category, files, folders)
