from django.test import Client


def test_get_package():
    client = Client()
    response = client.get("/package/minimatch/3.1.2")
    assert response.status_code == 200
    # SCC issue: this test fails! brace-expansion gets version 1.1.7, not 1.1.11 as the test
    #            expects (and 1.1.7 uses an earlier version of balanced-match).
    assert response.json() == {
        "dependencies": [
            {
                "dependencies": [
                    {"dependencies": [], "name": "balanced-match", "version": "1.0.2"},
                    {"dependencies": [], "name": "concat-map", "version": "0.0.1"},
                ],
                "name": "brace-expansion",
                "version": "1.1.11",
            }
        ],
        "name": "minimatch",
        "version": "3.1.2",
    }

# SCC issue: we should have more tests here. The Issue statement listed some interesting edge case
#       packages; at the very least, we should try those out, confirm we're happy with the behaviours
#       we see (or fix it if not!) and write scripts to expect those behaviours are maintained.
# - express:
#   - with code as is, this is fine: the minimum version doesn't have dependencies.
#   - later versions have unusual values, for example 3.7.0 has dependency "debug": "\u003E= 0.8.0 \u003C 1",
#   - also takes a long time to run, due to the number of dependencies and their heirarchy.
# - npm:
#   - with code as is, this is fine but slow - 45s
# - trucolor:
#   - appears to run indefinitely, either there's a loop (printing module names did show the same sequence repeatedly)
#     or there's a painful amount of repition
# - @snyk/snyk-docker-plugin
#   - fails at npm.py: versions = list(npm_package["versions"].keys()) due to npm_package not having that key - presumably
#     because this is an invalid entry string rather than because the crate is weird?