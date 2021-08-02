import argparse
import os
import pathlib


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--results", type=str, default='')
    parser.add_argument("-t", "--test", action='store_true', default=True)
    parser.add_argument("-l", "--list", action='store_false', default=False)
    parser.add_argument("-f", "--filter", type=str, default='')
    # parser.add_argument("-i", "--import", type=str, default='')
    # parser.add_argument("-e", "--export", type=str, default='')
    args = parser.parse_args()
    return args.results, args.test, args.list, args.filter


def restore_config(config_file, backup_file):
    if os.path.exists(backup_file):
        os.remove(config_file)
        os.rename(backup_file, config_file)
    if os.path.exists(backup_file):
        os.remove(backup_file)


def prepare_config(results_dir, config_file, backup_file):
    with open(config_file, 'r') as baseconfig_read:
        cfg_file_cnt = baseconfig_read.read()
    with open(backup_file, 'w') as baseconfig_backup_write:
        baseconfig_backup_write.write(cfg_file_cnt)
    with open(config_file, 'w') as baseconfig_write:
        baseconfig_write.write(cfg_file_cnt.replace("RESULTS_DIR = 'Results'", "RESULTS_DIR = '{}'".format(results_dir)))


if __name__ == '__main__':
    results_dir, test, list, filter = parse_arguments()
    base_path = os.path.join('{0}{1}..{1}libraries{1}'.format(os.path.dirname(__file__), os.path.sep))
    config_file = os.path.join(base_path, 'baseconfig.py')
    backup_file = os.path.join(base_path, 'baseconfig.py_bak')

    restore_config(config_file, backup_file)

    if results_dir:
        prepare_config(results_dir, config_file, backup_file)

    from testframework.libraries.config import config
    from testframework.libraries.logger import logger
    from testframework.engine.runner import run_tests
    run_tests(config, filter=filter)
