"""
devpi-server plugin hooks
-also see http://doc.devpi.net/latest/hooks.html
-find all currently supported hooks: devpi_server.hookspecs
-see log output in ~/.devpi/server/.xproc/devpi-server/xprocess.log
"""

from __future__ import unicode_literals

import datetime
import pickle
from pkg_resources import resource_filename
import PyRSS2Gen
from StringIO import StringIO

from devpi_server.log import threadlog
from devpi_web import description

server_url = None
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


def devpiserver_pyramid_configure(config, pyramid_config):
    """Called during initializing with the pyramid_config and the devpi_server config object."""
    global args_rss_no_auto
    debug("devpiserver_pyramid_configure called")
    pyramid_config.registry["rss_path"] = config.serverdir.join(".rss")
    info("server rss dir: %s" % pyramid_config.registry["rss_path"])
    args_rss_no_auto = config.args.rss_no_auto
    info("args_rss_no_auto: %s" % args_rss_no_auto)
    pyramid_config.include(__package__)


def devpiserver_cmdline_run(xom):
    """
    Return an integer with a success code (0 == no errors) if you handle the command line
    invocation, otherwise None. When the first plugin returns an integer, the remaining plugins
    are not called.
    """
    debug("devpiserver_cmdline_run called")
    if xom.config.args.theme is None:
        # use the small devpi_rss theme customization by default
        xom.config.args.theme = resource_filename(__package__, "")
        info("auto set web 'theme' to %s" % xom.config.args.theme)


def devpiserver_on_upload_sync(log, application_url, stage, project, version):
    """
    Called after release upload. Mainly to implement plugins which trigger external services like
    Jenkins to do something upon upload.
    """
    global server_url
    debug("devpiserver_pyramid_configure called")
    debug("application_url=%s, project=%s, version=%s" %
          (application_url, project, version))
    server_url = application_url


def devpiserver_on_upload(stage, project, version, link):
    """
    Called when a file is uploaded to a private stage for a project/version.
    link.entry.file_exists() may be false because a more recent revision deleted the file (and files
    are not revisioned). NOTE that this hook is currently NOT called for the implicit "caching"
    uploads to the pypi mirror.
    """
    debug("devpiserver_on_upload called")
    debug("project=%s, version=%s, link=%s" % (project, version, link))
    if ("rss_active" in stage.ixconfig) and (stage.ixconfig["rss_active"] in [False, "False"]):
        debug("rss not active for this index")
        return

    if not link.entry.file_exists():
        # taken from devpi_web.main.devpiserver_on_upload:
        # on replication or import we might be at a lower than
        # current revision and the file might have been deleted already
        warn("ignoring lost upload: %s", link)

    index_url = "%s/%s" % (server_url, stage.name)
    server_rss_dir = stage.xom.config.serverdir.join(".rss")
    xml_file = server_rss_dir.join("%s.xml" % stage.name.replace("/", "."))
    pickle_file = server_rss_dir.join("%s.pickle" % stage.name.replace("/", "."))

    if pickle_file.exists():
        debug("loading pickle file: %s" % pickle_file.strpath)
        with open(pickle_file.strpath, "r") as f:
            rss = pickle.load(f)
    else:
        debug("pickle file doesn't exist yet")
        rss = PyRSS2Gen.RSS2(title="Devpi index '%s'" % stage.name,
                             link=index_url,
                             description="The latest package uploads",
                             lastBuildDate=datetime.datetime.now())

    # apply some kinda max description text size
    _description = description.get_description(stage, project, version)
    if stage.xom.config.args.rss_truncate_desc:
        if _description.count("\n") > 32:
            debug("reducing amount of lines (%s)" % _description.count("\n"))
            _description = "\n".join(_description.splitlines(True)[:32] + ["[...]"])
        if len(_description) > 1024:
            debug("reducing amount of characters (%s)" % len(_description))
            _description = _description[:1024] + "[...]"

    while len(rss.items) >= stage.xom.config.args.rss_max_items:
        debug("reducing number of rss items (%s)" % len(rss.items))
        rss.items.pop()

    rss.items.insert(0, PyRSS2Gen.RSSItem(
        title="%s %s" % (project, version),
        link="%s/%s/%s" % (index_url, project, version),
        description=_description,
        guid=PyRSS2Gen.Guid("%s/%s/%s" % (index_url, project, version)),
        pubDate=datetime.datetime.now()))

    if not server_rss_dir.exists():
        debug("creating server rss dir: %s" % server_rss_dir.strpath)
        server_rss_dir.mkdir()

    debug("writing xml file: %s" % xml_file.strpath)
    rss.write_xml(open(xml_file.strpath, "w"), encoding="utf-8")

    with open(pickle_file.strpath, "w") as f:
        debug("writing pickle file: %s" % pickle_file.strpath)
        s = StringIO()
        pickle.dump(rss, s)
        f.write(s.getvalue())


def includeme(config):
    info("adding rss view")
    config.add_route("get_rss", "/{user}/{index}/+rss")
    config.scan()


def info(msg):
    threadlog.info("devpi-rss: %s" % msg)


def warn(msg):
    threadlog.warn("devpi-rss: %s" % msg)


def debug(msg):
    threadlog.debug("devpi-rss: %s" % msg)
