import re

raw_version_pattern = r"""
    ^
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release
        (?P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
    $
"""
raw_requirement_pattern = r"""
    (?P<name>[a-z0-9\[\]]+(?:[a-z0-9-_.])*)+               # package name
    (?P<clauses>.*)                                        # comma-separated list of clauses
"""
version_pattern = re.compile(raw_version_pattern, re.VERBOSE | re.IGNORECASE)
requirement_pattern = re.compile(raw_requirement_pattern, re.VERBOSE | re.IGNORECASE)
version_separators = re.compile(r"[._-]")
