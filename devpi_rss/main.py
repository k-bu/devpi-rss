"""
-devpi-server plugin hooks
-Also see http://doc.devpi.net/latest/hooks.html
-Find all currently supported hooks: devpi_server.hookspecs
-See log output in ~/.devpi/server/.xproc/devpi-server/xprocess.log
"""

from __future__ import unicode_literals

import datetime
import os
import pickle
from pkg_resources import resource_filename
from pyramid.response import FileResponse, Response
import PyRSS2Gen
from StringIO import StringIO

from devpi_server.log import threadlog
from devpi_web import description

server_url = None
server_rss_dir = None
args_rss_no_auto = False


def devpiserver_add_parser_options(parser):
    """
    Called before command line parsing to allow plugins to add options through a call to
    parser.add_argument().
    """
    option_group = parser.addgroup("rss options")
    option_group.addoption("--rss-max-items", type=int, default=50,
                           help="maximum number of stored feed items")
    option_group.addoption("--rss-truncate-desc", action="store_true",
                           help="do not let descriptions exceed 32 lines or 1024 characters")
    option_group.addoption("--rss-no-auto", action="store_true",
                           help="do not automatically activate rss for new indices")


def devpiserver_indexconfig_defaults(index_type):
    """
    Returns a dictionary with keys and their defaults for the index configuration dictionary. It's a
    good idea to use the plugin name as prefix for the key names to avoid clashes between key names
    in different plugins.
    """
    debug("devpiserver_indexconfig_defaults called")
    return {"rss_active": not args_rss_no_auto}


def get_rss(request):
    xml_fname = "%s.xml" % request.path[1:].replace("/+rss", "").replace("/", ".")
    xml_fname = os.path.join(server_rss_dir, xml_fname).replace("\\", "/")
    if os.path.exists(xml_fname):
        return FileResponse(xml_fname)
    else:
        return Response("No uploads for this index yet..")


def devpiserver_pyramid_configure(config, pyramid_config):
    """Called during initializing with the pyramid_config and the devpi_server config object."""
    global server_rss_dir, args_rss_no_auto
    debug("devpiserver_pyramid_configure called")
    server_rss_dir = os.path.join("%s" % config.serverdir, ".rss")
    info("server_rss_dir: %s" % server_rss_dir)
    args_rss_no_auto = config.args.rss_no_auto
    info("args_rss_no_auto: %s" % args_rss_no_auto)
    info("adding rss view")
    pyramid_config.add_route("get_rss", "/{user}/{index}/+rss")
    pyramid_config.add_view(get_rss, route_name="get_rss")


def devpiserver_cmdline_run(xom):
    """
    Return an integer with a success code (0 == no errors) if you handle the command line
    invocation, otherwise None. When the first plugin returns an integer, the remaining plugins
    are not called.
    """
    if xom.config.args.theme is None:
        # use the small devpi_rss theme customization by default
        xom.config.args.theme = resource_filename(__package__, "")
        info("auto set web 'theme' to %s" % xom.config.args.theme)


def devpiserver_on_upload_sync(log, application_url, stage, projectname, version):
    """
    Called after release upload. Mainly to implement plugins which trigger external services like
    Jenkins to do something upon upload.
    """
    global server_url
    debug("devpiserver_pyramid_configure called")
    debug("application_url=%s, projectname=%s, version=%s" %
          (application_url, projectname, version))
    server_url = application_url


def devpiserver_on_upload(stage, projectname, version, link):
    """
    Called when a file is uploaded to a private stage for a projectname/version.
    link.entry.file_exists() may be false because a more recent revision deleted the file (and files
    are not revisioned). NOTE that this hook is currently NOT called for the implicit "caching"
    uploads to the pypi mirror.
    """
    debug("devpiserver_on_upload called")
    debug("projectname=%s, version=%s, link=%s" % (projectname, version, link))
    if ("rss_active" in stage.ixconfig) and (stage.ixconfig["rss_active"] in [False, "False"]):
        debug("rss not active for this index")
        return

    if not link.entry.file_exists():
        # taken from devpi_web.main.devpiserver_on_upload:
        # on replication or import we might be at a lower than
        # current revision and the file might have been deleted already
        warn("ignoring lost upload: %s", link)

    index_url = "%s/%s" % (server_url, stage.name)
    xml_fname = os.path.join(server_rss_dir, "%s.xml" % stage.name.replace("/", "."))
    pickle_fname = os.path.join(server_rss_dir, "%s.pickle" % stage.name.replace("/", "."))

    if os.path.exists(pickle_fname):
        with open(pickle_fname, "r") as f:
            rss = pickle.load(f)
    else:
        rss = PyRSS2Gen.RSS2(title="Devpi index '%s'" % stage.name,
                             link=index_url,
                             description="The latest package uploads",
                             lastBuildDate=datetime.datetime.now())

    # apply some kinda max description text size
    _description = description.get_description(stage, projectname, version)
    if stage.xom.config.args.rss_truncate_desc:
        if _description.count("\n") > 32:
            _description = "\n".join(_description.splitlines(True)[:32] + ["[...]"])
        elif len(_description) > 1024:
            _description = _description[:1024] + "[...]"

    while len(rss.items) >= stage.xom.config.args.rss_max_items:
        rss.items.pop()

    rss.items.insert(0, PyRSS2Gen.RSSItem(
        title="%s %s" % (projectname, version),
        link="%s/%s/%s" % (index_url, projectname, version),
        description=_description,
        guid=PyRSS2Gen.Guid("%s/%s/%s" % (index_url, projectname, version)),
        pubDate=datetime.datetime.now()))

    rss.write_xml(open(xml_fname, "w"))

    with open(pickle_fname, "w") as f:
        s = StringIO()
        pickle.dump(rss, s)
        f.write(s.getvalue())


def info(msg):
    threadlog.info("devpi-rss: %s" % msg)


def warn(msg):
    threadlog.warn("devpi-rss: %s" % msg)


def debug(msg):
    threadlog.debug("devpi-rss: %s" % msg)
