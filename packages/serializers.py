from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField


class PackageSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    # SCC issue: this used to return a description field, but that's
    #            been removed. Is this intentional? If so, why are we
    #            still keeping the description field in the rest of the
    #            code?
    version = serializers.CharField()
    # SCC issue: we've lost information here, the value we used to return
    #            was the range supported and now we provide a specific
    #            version (^15.6.2 => 15.6.2). This makes sense from the
    #            perspective of "this is the version you'll actually use"
    #            and it's necessary given we're then getting the recursive
    #            dependencies of that one partiuclar version, but was there
    #            value in the info about what the using module asked for and
    #            could support?  Should we provide both?
    #    EDIT: see wider concern about approach and which versions we should
    #          be using mentioned in my comments in modules/npm.py get_package()
    dependencies = serializers.ListSerializer(child=RecursiveField())
