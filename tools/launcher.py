#!/usr/bin/python
""" Script to launch maptool """
import subprocess
import os
import logging
import sys
import argparse
import shutil

LOGGER = logging.getLogger()
HANDLER = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)


def main():
    """ Main function """
    working_dir = r'/tmp'
    if os.name == 'nt':
        working_dir = r'c:\tmp'
    
    parser = argparse.ArgumentParser(description='A tool to synchronize maptool campaign files.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('campaign', action='store', help='Campaign name.')
    parser.add_argument('-g', '--game-name', action='store', help='Game name.', default='pathfinder')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode.')
    parser.add_argument('-w', '--working-dir', action='store', help='Working directory.', default=working_dir)
    # parser.add_argument('-m', '--maptool-dir', action='store', help='Maptool directory.', required=True)

    args = parser.parse_args()

    if args.verbose:
        LOGGER.setLevel(logging.DEBUG)
        
    repo_base_dir = os.path.realpath(os.path.join(os.getcwd(), ".."))
    LOGGER.debug(repo_base_dir)
    campaign_base_dir = os.path.realpath(os.path.join(repo_base_dir, "campaigns", args.game_name, args.campaign))
    LOGGER.debug(campaign_base_dir)
    if not os.path.exists(campaign_base_dir) or not os.path.isdir(campaign_base_dir):
        LOGGER.error("No campaign name %s exists (%s directory doesn't exists)" % (args.campaign, campaign_base_dir))
    else:
        LOGGER.info("Try to update selected campaign (git pull from %s)" % (campaign_base_dir))
        g_cmd = subprocess.Popen('git pull', shell=True, cwd=campaign_base_dir)
        g_cmd.wait()
        tmp_archive_path = os.path.join(args.working_dir, '_'.join([args.game_name, args.campaign]))
        LOGGER.info("Create temporary archive: %s.cmpgn" % (tmp_archive_path))
        shutil.make_archive(tmp_archive_path, 'zip', campaign_base_dir)
      
        try:
            os.rename(tmp_archive_path + '.zip', tmp_archive_path + '.cmpgn')
        except OSError, error:
            try:
                os.remove(tmp_archive_path + '.cmpgn')
            except Exception, error:
                LOGGER.error("Cannot create %s file. Is it opened ?" % (tmp_archive_path + '.cmpgn'))
                return
            os.rename(tmp_archive_path + '.zip', tmp_archive_path + '.cmpgn')
            
    
    # TODO:  
    # - Launch maptool with campaing file.
    # - Uncompress file in repo
    # - git add -A & git push
    # - Delete tmp archive file
      


if __name__ == "__main__":
    main()
