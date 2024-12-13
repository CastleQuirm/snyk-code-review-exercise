class VersionedPackage:
    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        # SCC issue: currently the dependencies parameter is never used by the callers, in which case we shouldn't
        #       have this parameter at all. However, the callers then go on to create the lists themselves immediately
        #       afterwards, so it'd probably be nicer to actually inline those and have this be used.
        #       Those callers can also reliably provide an empty list rather than None, so we should ditch the option
        #       aspect here and just take a list without a default.        
        dependencies: list["VersionedPackage"] | None = None
    ):
        self.name = name
        self.version = version
        self.description = description
        self.dependencies = dependencies or []
