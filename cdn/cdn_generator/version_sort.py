def version_sort(s):
    """
    Sort a list of versions based on the way OpenTTD versions the releases.

    This is always one of the following:
     - 1.2.3-alpha1
     - 1.2.3-beta2
     - 1.2.3-RC3
     - 1.2.3

    This function sorts this in that order (beta before RC before stable).
    """
    version, _, preversion = s.partition("-")

    # This works because 'alpha' < 'beta' < 'rc' < 'stable'. It is a bit cheating.
    preversion = preversion.lower()
    if not preversion:
        preversion = "stable"

    # There are some versions like 0.4.0.1, that needs special attention.
    # We solve it by making this [0, 4, 0, "stable1"], which sorts correctly.
    versions = version.split(".")
    if len(version) > 3:
        preversion += str(versions[3:])
        versions = versions[0:3]

    return list(map(int, versions)) + [preversion]
