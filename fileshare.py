import logging
from errbot import botcmd, BotPlugin
from config import BOT_DATA_DIR
from os import path, mkdir, walk
from io import open
import shutil

FILESHARE_PATH = path.join(BOT_DATA_DIR, "public")

if not path.exists(FILESHARE_PATH):
    mkdir(FILESHARE_PATH)


class FileShare(BotPlugin):
    min_err_version = '2.2.0-beta' # for file transfers

    def target(self, name):
        full_path = path.join(FILESHARE_PATH, name)
        if full_path != path.abspath(full_path):
            logging.warn('Refused the filename "%s" is it an injection attempt?' % name)
            return ''
        return full_path

    def callback_stream(self, stream):
        if not stream.name:
            logging.info("Anonymous stream, I can't save that")
            return

        logging.debug('Receive the file "%s"' % stream.name)
        destination_path = self.target(stream.name)
        if not destination_path:
            self.send(stream.identity, "Invalid filename %s." % stream.name)
            return
        with open(destination_path, "wb") as destination:
            shutil.copyfileobj(stream, destination)
        self.send(stream.identity, "File %q well received." % stream.name)


    @botcmd
    def download(self, mess, args):
        target = self.target(args)
        if not target:
            return 'Invalid filename "%s"' % target

        if not path.exists(target):
            return 'File not found %s' % args
        self.send_stream_request(mess.frm, open(target, 'rb'), name=args, size=path.getsize(target))
        return 'File request sent'

    @botcmd
    def ls(self, mess, args):
        return '\n'.join(['\n'.join([n for n in f]) for p, _, f in walk(FILESHARE_PATH)])
