from rest_framework import renderers, views
from rest_framework.request import Request
from rest_framework.response import Response

from packages.modules import npm
from packages.serializers import PackageSerializer


class PackageView(views.APIView):
    renderer_classes = [renderers.JSONRenderer]

    def get(self, request: Request, package_name: str, range: str | None = None):
        if range is None:
            range = "*"

        # SCC aside: this doesn't sanitise inputs and Snyk spots and highlights this
        #       - but this isn't added in this PR! That said: raising flagging because
        #       we might want to add sanitisation at other points (see comment later in
        #       get_package()) but it could make sense to have a common approach shared
        #       here.
        package_info = npm.get_package(package_name, range, package_list={})
        serializer = PackageSerializer(package_info)
        return Response(serializer.data)
