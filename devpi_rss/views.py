from devpi_web.views import ContextWrapper
from pyramid.response import FileResponse, Response
from pyramid.view import view_config


@view_config(route_name="get_rss", request_method="GET")
def get_rss(context, request):
    xml_fname = "%s.xml" % ContextWrapper(context).stage.name.replace("/", ".")
    xml_fname = request.registry["rss_path"].join(xml_fname)
    if not xml_fname.exists():
        return Response("The RSS feed of this index has not recorded any uploads yet.")
    return FileResponse(xml_fname.strpath.replace("\\", "/"))
