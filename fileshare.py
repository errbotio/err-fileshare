import logging
import shutil
from io import open
from os import mkdir, path, walk

from config import BOT_DATA_DIR
from errbot import BotPlugin, botcmd

FILESHARE_PATH = path.join(BOT_DATA_DIR, "public")

if not path.exists(FILESHARE_PATH):
    mkdir(FILESHARE_PATH)

LOG = logging.getLogger("errbot.plugin.fileshare")


class FileShare(BotPlugin):
    def target(self, name):
        full_path = path.join(FILESHARE_PATH, name)
        if full_path != path.abspath(full_path):
            LOG.warn("Refused the filename '%s' is it an injection attempt?", name)
            return ""
        return full_path

    def callback_stream(self, stream):
        if not stream.name:
            LOG.info("Anonymous stream, I can't save that")
            return

        LOG.debug("Receive the file '%s'", stream.name)
        destination_path = self.target(stream.name)
        if not destination_path:
            self.send(stream.identity, f"Invalid filename {stream.name}.")
            return
        with open(destination_path, "wb") as destination:
            shutil.copyfileobj(stream, destination)
        self.send(stream.identity, f"File {stream.name} well received.")

    @botcmd
    def download(self, mess, args):
        target = self.target(args)
        if not target:
            return f"Invalid filename '{target}'"

        if not path.exists(target):
            return f"File not found {args}"
        self.send_stream_request(
            mess.frm, open(target, "rb"), name=args, size=path.getsize(target)
        )
        return "File request sent"

    @botcmd
    def ls(self, mess, args):
        return "\n".join(
            ["\n".join([n for n in f]) for p, _, f in walk(FILESHARE_PATH)]
        )
