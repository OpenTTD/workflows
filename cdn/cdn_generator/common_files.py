import pathlib
import shutil


def generate_common_files():
    """
    Copy a bunch of static files into the generated folder.

    This means they are copied to the CDN too on next sync. They are
    technically not generated, but creating a second flow just for these
    files doesn't make sense.
    """

    pathlib.Path("generated").mkdir(parents=True, exist_ok=True)
    shutil.copyfile("config.yaml", "generated/config.yaml")
    shutil.copyfile("README.md", "generated/README.md")

    pathlib.Path("generated/errors").mkdir(parents=True, exist_ok=True)
    shutil.copyfile("errors/404.html", "generated/errors/404.html")

    with open("generated/robots.txt", "w") as f:
        f.write("\n".join(["User-agent: *", "Disallow: /"]) + "\n")
