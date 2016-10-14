#!/usr/bin/python
""" Script to launch maptool """
import subprocess
import os
import logging
import sys
import argparse
import shutil
import zipfile

LOGGER = logging.getLogger()
HANDLER = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)

def find_jar(path, jar_name):
    """ Find a .jar file

    Keyword arguments:
    path     -- the root directory to search in
    jar_name -- the name that should be contains in the jar name
    """
    for root, dirs, files in os.walk(path):
        LOGGER.debug("find_jar: Look in %s", root)
        for _file in files:
            file_name, file_extension = os.path.splitext(_file)
            LOGGER.debug("find_jar: Look for %s%s", file_name, file_extension)
            if file_extension == ".jar" and jar_name in file_name:
                return _file


def main():
    """ Main function """
    working_dir = r'/tmp'
    if os.name == 'nt':
        working_dir = r'c:\tmp'
    
    parser = argparse.ArgumentParser(description='A tool to synchronize maptool campaign files.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('campaign', action='store', help='Campaign name.')
    parser.add_argument('-m', '--maptool-dir', action='store', help='Maptool directory.', required=True)
    parser.add_argument('-g', '--game-name', action='store', help='Game name.', default='pathfinder')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode.')
    parser.add_argument('-w', '--working-dir', action='store', help='Working directory.', default=working_dir)
    parser.add_argument('-l', '--use-launcher', action='store_true', help='Use maptool launcher.', default=False)
    parser.add_argument('-p', '--push-modifications', action='store_true', help='Push modifications (git push).', default=False)
    parser.add_argument('-r', '--read-only', action='store_true', help='Read only mode.')

    args = parser.parse_args()

    if args.verbose:
        LOGGER.setLevel(logging.DEBUG)
        
    repo_base_dir = os.path.realpath(os.path.join(os.getcwd(), ".."))
    LOGGER.debug(repo_base_dir)
    campaign_base_dir = os.path.realpath(os.path.join(repo_base_dir, "campaigns", args.game_name, args.campaign))
    LOGGER.debug(campaign_base_dir)
    if not os.path.exists(campaign_base_dir) or not os.path.isdir(campaign_base_dir):
        LOGGER.error("No campaign name %s exists (%s directory doesn't exists)", args.campaign, campaign_base_dir)
    else:
        LOGGER.info("Try to update selected campaign (git pull from %s)", campaign_base_dir)
        g_cmd = subprocess.Popen('git pull', shell=True, cwd=campaign_base_dir)
        g_cmd.wait()
        tmp_archive_path = os.path.join(args.working_dir, '_'.join([args.game_name, args.campaign]))
        LOGGER.info("Create temporary archive: %s.cmpgn", tmp_archive_path)
        shutil.make_archive(tmp_archive_path, 'zip', campaign_base_dir)
      
        try:
            os.rename(tmp_archive_path + '.zip', tmp_archive_path + '.cmpgn')
        except OSError, error:
            try:
                os.remove(tmp_archive_path + '.cmpgn')
            except Exception, error:
                LOGGER.error("Cannot create %s file. Is it opened ?", tmp_archive_path + '.cmpgn')
                return -1
            os.rename(tmp_archive_path + '.zip', tmp_archive_path + '.cmpgn')

        jar_name = "maptool"
        if args.use_launcher:
            jar_name = "launcher"
        maptool_jar = find_jar(args.maptool_dir, jar_name)
        if maptool_jar is None:
            LOGGER.error("Cannot find %s jar in %s", jar_name, args.maptool_dir)
            return -1
        LOGGER.debug(maptool_jar) 
        maptool_cmd = 'java -Xms64M -Xmx2048M -Xss4M -jar ' + maptool_jar
        LOGGER.info("Launch maptool with command %s in %s", maptool_cmd, args.maptool_dir)
        g_cmd = subprocess.Popen(maptool_cmd, shell=True, cwd=args.maptool_dir)
        g_cmd.wait()

        if not args.read_only:
            LOGGER.info("Uncompress file %s in %s", tmp_archive_path + '.cmpgn', campaign_base_dir)
            zip_file = zipfile.ZipFile(tmp_archive_path + '.cmpgn')
            zip_file.extractall(campaign_base_dir)
            zip_file.close()

            LOGGER.info("Add campaign file to git (git add -A)")
            g_cmd = subprocess.Popen('git add -A .', shell=True, cwd=campaign_base_dir)
            g_cmd.wait()

            LOGGER.info("Commit modifications(git commit -m)")
            g_cmd = subprocess.Popen('git commit -m "Update campaign %s"' % args.campaign, shell=True, cwd=campaign_base_dir)
            g_cmd.wait()
            
            if args.push_modifications:
                LOGGER.info("Push modifications(git push)")
                g_cmd = subprocess.Popen('git push', shell=True, cwd=campaign_base_dir)
                g_cmd.wait()
    
    # TODO:  
    # - Launch maptool with campaing file.
    # - Delete tmp archive file
    return 0


if __name__ == "__main__":
    sys.exit(main())
