import requests
import semver

from packages.models import VersionedPackage

NPM_REGISTRY_URL = "https://registry.npmjs.org"


def get_package(name: str, range: str) -> VersionedPackage:
    url = f"{NPM_REGISTRY_URL}/{name}"

    # SCC issue - what happens if this fails? Can we do something better/more useful than just crash?
    npm_package = requests.get(url).json()

    # SCC nitpick - using two very similarly named variables can be an issue (versions vs version).  Since we aren't
    #         using versions after the following line, it would probably be better to just inline the definition and
    #         only have 'version' (and version_record').
    versions = list(npm_package["versions"].keys())

    # SCC major - how did you pick 'min_satisfying' to choose which version in the range to look at? This is going to
    #        ensure we get the earliest valid option - but if a user had a later version of the dependency that met the
    #        criteria, they'd get the wrong set of results.
    #        This is a tricky problem to solve and one that will need to be tackled at the spec level, since the Issue
    #        doesn't define what we should do here. Should we always pick the oldest and miss telling users about more
    #        recent versions' bugs and fixes? Always pick the newest and not warn users who haven't updated?  Support
    #        getting the entire range and having an exponentially expanding problem space?  Make it configurable?
    # SCC issue - the value of range here is a string we've received from either the caller or from the NPM over the
    #        internet, with no validation. We should ensure this is correctly formatted.
    version = semver.min_satisfying(versions, range)
    version_record = npm_package["versions"][version]

    package = VersionedPackage(
        name=version_record["name"],
        version=version_record["version"],
        description=version_record["description"],
    )
    dependencies = version_record.get("dependencies", {})

    # SCC major - running this recursively over every dependency can lead to a huge amount of repetition: e.g. if A
    #        depends on B and C, and both B and C depend on D which has some massive chain, we duplicate the work
    #        for D all the way down its chain. As raised in the issue, we should consider caching results to avoid
    #        duplication between multiple requests, either from different top level requests or within a single 
    #        dependency chain
    # SCC major - we don't have any protection from infinite loops (although we'd hope there's some protection against
    #        that in the actual package manager?)
    # SCC major - there's no handling of asynchronous requests here - we request synchronously for every child (and from
    #        there every further descendant dependency). This can be very slow and inefficient!
    
    package.dependencies = [
        get_package(name=dep_name, range=dep_range) for dep_name, dep_range in dependencies.items()
    ]

    return package


# SCC issue - returning a tuple is generally a minor code smell - it's not always wrong but there's usually
#       a neater way to write it. In this case, why are we returning the dependencies seperately from the
#       VersionedPackage struct that has space to hold them? We can add them on creation, return a single
#       object, and then access them from that object in the caller if we need.
# SCC issue - additionally - do we need this function? It appears to be the old behaviour (no recursive call
#       for dependencies), but with no way to access it?
def request_package(name: str, range: str) -> tuple[VersionedPackage, dict]:
    url = f"{NPM_REGISTRY_URL}/{name}"

    npm_package = requests.get(url).json()

    versions = list(npm_package["versions"].keys())
    version = semver.min_satisfying(versions, range)
    version_record = npm_package["versions"][version]

    return VersionedPackage(
        name=version_record["name"],
        version=version_record["version"],
        description=version_record["description"],
    ), version_record.get("dependencies", {})
