# Content Delivery Network

OpenTTD publishes all the binaries produced to a CDN.
This CDN is hosted by AWS CloudFront, which fetches the files from a private AWS S3.
There are a various amount of files on the CDN to help with automation and human readability.

## index.html

AWS S3 has no ability to do directory listing.
From experience, OpenTTD has found out that a CDN without being able to browse files, often leads to frustration by its end users.
As such, part of the `cdn-generator` is to create `index.html` files in every folder.
It does a few tricks, like sorting by version and like putting the newest version on top, to make it more useful.
By publishing this `index.html` on the CDN, it feels like there is directory listing enabled.
It really isn't.

## folders.yaml

Similar to `index.html`, but with only the folders, and in a format that can easily be automated.

## manifest.yaml

Every release has a `manifest.yaml`, which contains all the important parts of the release.
Automation can use this file to know what file to download, or what size to expect.
There are also checksum values there to validate a download.

## latest.yaml

For automation, you often want to know: what is the latest release.
In the root folder and every subfolder there-of, there is a `latest.yaml` indicating exactly this.
Per category, there are two choices: either it is "releases" or something else.
In case of the first, there can be a "stable" and "testing" version.
Otherwise there is always one.
There are several keys per entry:

- `version`: indicates the latest version.
- `name`: indicates if it is stable/testing (in case of "releases") or what type this is ("master", "trunk", "nightly", ..).
- `category`: the category this entry belongs to.
- `date`: the date when this version was released.
- `folder`: in which folder thie version can be found, relative to `latest.yaml`.

In the root, all `latest.yaml` from the children are combined together.

## config.yaml

In the root there is a `config.yaml`.
This tells the `cdn-generator` which folders to index, and how to do this exactly.
There are several keys per entry:

- `name`: name of the folder to configure.
- `subfolders`: optional (default: none).
  - `per-name`: the name of the subfolder is just a name, and the versions are a subfolder of those folders.
  - `per-year`: the subfolder is split per year.
- `override-name`: optional (default: use `name`).
  - `nightly`: force the name to be "nightly".
  - `in-folder-name`: folder should be named `XXX-NAME-XXX`, and the name is the `NAME` part.
- `sort`: optional (default: `version`).
  - `normal`: use "abc" sorting.
  - `version`: use version sorting: "1.9-alpha1" < "1.9-beta2" < "1.9-RC3" < "1.9" < "1.10".
