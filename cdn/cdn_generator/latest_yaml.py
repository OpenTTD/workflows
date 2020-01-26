import pathlib

from cdn_generator.helpers import (
    list_folder,
    get_content,
    get_name,
)


def _find_latest_version(prefix, config):
    is_version_folder = config.get("sort") != "normal"
    base_category = "-".join(prefix.split("-")[:-1])

    _, folders = list_folder(prefix, is_version_folder=is_version_folder)
    folders.reverse()

    if not folders:
        return []

    latest_versions = []

    if is_version_folder:
        # Find the first folder that is testing ("-RCN", "-betaN")
        for folder in folders:
            if "-" in folder:
                testing = folder
                break
        else:
            testing = None

        # Find the first folder that is stable (so without any postfix)
        for folder in folders:
            if "-" not in folder:
                stable = folder
                break
        else:
            stable = None

        if stable:
            date_stable = get_content(f"{prefix}/{stable}/released.txt").replace(" ", "T").replace("TUTC", ":00-00:00")
            latest_versions.append(
                {"version": stable, "name": "stable", "category": base_category, "date": date_stable,}
            )

        if testing:
            date_testing = (
                get_content(f"{prefix}/{testing}/released.txt").replace(" ", "T").replace("TUTC", ":00-00:00")
            )

            # There is only a testing if the stable is older
            if stable and date_stable < date_testing:
                latest_versions.append(
                    {"version": testing, "name": "testing", "category": base_category, "date": date_testing,}
                )

    else:
        name = get_name(folders[0], config)

        date = get_content(f"{prefix}/{folders[0]}/released.txt").replace(" ", "T").replace("TUTC", ":00-00:00")
        latest_versions.append(
            {"version": folders[0], "name": name, "category": base_category, "date": date,}
        )

    return latest_versions


def write_latest_yaml(prefix, latest_versions):
    latest_content = ["latest:"]
    for item in latest_versions:
        latest_content.append(f"- version: {item['version']}")
        for key, value in item.items():
            if key == "version":
                continue

            latest_content.append(f"  {key}: {value}")

    pathlib.Path(f"generated/{prefix}").mkdir(parents=True, exist_ok=True)
    with open(f"generated/{prefix}/latest.yaml", "w") as f:
        f.write("\n".join(latest_content) + "\n")


def generate_latest_yaml(prefix, config, filter_path=None):
    print(f"Creating latest.yaml for {prefix} ...")

    skip_write = filter_path and not filter_path.startswith(f"{prefix}/")
    subfolders = config.get("subfolders")

    if subfolders is None:
        latest_versions = _find_latest_version(prefix, config)
    elif subfolders == "per-year":
        _, folders = list_folder(prefix)
        # The latest folder should be the latest year
        latest_versions = _find_latest_version(f"{prefix}/{folders[-1]}", config)
        for item in latest_versions:
            item["folder"] = folders[-1]
    elif subfolders == "per-name":
        old_subfolders = config["subfolders"]
        config["subfolders"] = None

        latest_versions = []

        # Generate a latest.yaml per subfolder
        _, folders = list_folder(prefix)
        for folder in folders:
            subfolder_versions = generate_latest_yaml(f"{prefix}/{folder}", config, filter_path=filter_path)
            for item in subfolder_versions:
                item["folder"] = folder
            latest_versions.extend(subfolder_versions)

        config["subfolders"] = old_subfolders
    else:
        raise Exception("Unknown subfolders type '{subfolders}'")

    if not skip_write:
        write_latest_yaml(prefix, latest_versions)

    return latest_versions
