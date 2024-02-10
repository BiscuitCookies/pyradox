import _initpath
import os, re, sys

import pyradox
import fileinput

class GameFileValidator():
    """ search_typical_folders_for_utf8() can be used to find utf8 lines
        in files which should use the ANSI/cp1252 encoding """

    def __init__(self, root_folder):
        self.root_folder = root_folder

        # this regex has the shortcomming that it does not ignore an # inside a quote
        self.remove_comment_re = re.compile('#.*')

    def search_file_for_utf8(self, filename, ignore_comments = True, dry_run = True):
        """ detect utf8 lines by interpreting the lines as cp1252
            and utf8 and output lines which differ.
            Lines which can't be parsed as utf8 are ignored and lines which can't
            be parsed as cp1252 are output with a different error message"""

        with open(filename, 'r+b') as file:
            lineno = 0
            file_changed = False
            lines = []

            for line in file:
                lineno += 1
                try:
                    cp1252string = str(line, 'cp1252')
                except UnicodeDecodeError:
                    print("non1252 line {} found in {}. Ignoring invalid characters".format(lineno, filename), file=sys.stderr)
                    print(line, file=sys.stderr)
                    cp1252string = str(line, 'cp1252', errors='ignore')
                try:
                    utf8string = str(line, 'utf8')
                    if ignore_comments:
                        cp1252string_to_compare = self.remove_comment_re.sub('', cp1252string)
                        utf8string_to_compare = self.remove_comment_re.sub('', utf8string)
                    else:
                        cp1252string_to_compare = cp1252string
                        utf8string_to_compare = utf8string
                    if utf8string_to_compare != cp1252string_to_compare:
                        print("Possible utf8 line {} found in {}".format(lineno, filename), file=sys.stderr)
                        print('utf8: {}'.format(utf8string), end='', file=sys.stderr)
                        print('1252: {}'.format(cp1252string), end='', file=sys.stderr)
                        print('-------------------------------------------------------', file=sys.stderr)
                        if not dry_run:
                            try:
                                line = utf8string.encode('cp1252')
                                file_changed = True
                            except UnicodeEncodeError:
                                print("line {} in \"{}\" can't be represented as cp1252".format(lineno, filename), file=sys.stderr)
                                print(line, file=sys.stderr)

                except UnicodeDecodeError:
                    pass # so its not utf8

                lines.append(line)
            if file_changed and not dry_run:
                file.seek(0)
                file.truncate()
                for line in lines:
                    file.write(line)

    def search_folder_for_utf8(self, folder, ignore_comments = True, dry_run = True):
        for root, dirs, files in os.walk(os.path.join( self.root_folder, folder)):
            for filename in files:
                self.search_file_for_utf8(os.path.join(root, filename), ignore_comments, dry_run)

    def search_typical_folders_for_utf8(self, ignore_comments = True, dry_run = True):
        for folder in ['common', 'decisions', 'events', 'history', 'missions']:
            self.search_folder_for_utf8(folder, ignore_comments, dry_run)


if __name__ == '__main__':
    eu4_install_folder = pyradox.get_game_directory('EU4')
    validator = GameFileValidator(eu4_install_folder)
    validator.search_typical_folders_for_utf8(ignore_comments = False, dry_run = True)

