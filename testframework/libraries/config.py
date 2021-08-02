import os
from datetime import datetime
from glob import glob
import configparser
import testframework.libraries.baseconfig as baseconfig


class Config:
    def __init__(self, config_path=None, reversed_config=False):
        self.path_to_config = config_path
        self.reversed_order_of_config = reversed_config
        self.custom_results_dir_prefix = None

    def set_custom_results_dir_prefix(self, prefix):
        self.custom_results_dir_prefix = prefix

    def _read_config(self):
        # reversed == True -> if you want to have deepest config file
        # value written on top of all [previous] configs
        global_config = {}
        all_configs = []

        if not self.path_to_config:
            self.path_to_config = os.getcwd()
        config_files = glob("{}/**/*conf*.ini".format(self.path_to_config), recursive=True)
        config_files = sorted(config_files, reverse=self.reversed_order_of_config)
        cfg = configparser.ConfigParser()
        for cfg_file in config_files:
            cfg.read(cfg_file)
            if cfg.sections():
                _config = {}
                for k in cfg.keys():
                    if k not in _config:
                        _config[k] = {}
                    for v_k in cfg[k].keys():
                        if v_k not in _config[k]:
                            _config[k][v_k] = cfg[k][v_k]
                all_configs.append({'src': cfg_file, 'config': _config})
        for config in all_configs:
            keys = [key for key in config['config'].keys() if key != 'DEFAULT']
            for _cfg_key in keys:
                if _cfg_key not in global_config:
                    global_config[_cfg_key] = config['config'][_cfg_key]
                for k in config['config'][_cfg_key].keys():
                    if k not in global_config[_cfg_key]:
                        global_config[_cfg_key][k] = \
                            config['config'][_cfg_key][k]
        sorted_keys = sorted(global_config.keys())
        return {k: global_config[k] for k in sorted_keys}

    def __prepare_regex(self, in_regex):
        return '^{}$'.format(in_regex.replace('*', '.*')) \
            if any([True for char in in_regex if char in ['*', '.']]) \
            else '^{}.*$'.format(in_regex)

    def get_configuration(self):
        config = self._read_config()

        def get_value_from_config(cfg_dictionary, path):
            keys = path.split(':')
            if keys[0] in cfg_dictionary:
                if keys[1] in cfg_dictionary[keys[0]]:
                    return cfg_dictionary[keys[0]][keys[1]]
            # if not found in config dictionary -
            # just return hardcoded values
            # from testframework.libraries.baseconfig
            return getattr(baseconfig, keys[1].upper())

        results_dir = get_value_from_config(config, 'GLOBAL:results_dir')
        log_file = get_value_from_config(config, 'LOGGING:log_file')
        custom_results_dir_prefix = get_value_from_config(config, 'GLOBAL:custom_results_dir_prefix')
        class_regex = get_value_from_config(config, 'GLOBAL:class_regex')
        file_regex = get_value_from_config(config, 'GLOBAL:file_regex')
        method_regex = get_value_from_config(config, 'GLOBAL:method_regex')
        timestamp_format = get_value_from_config(config, 'FORMATS:timestamp_format')

        # part of code which will take care of cmd line args, not yet though
        # if not custom_results_dir_prefix:
        #     if self.custom_results_dir_prefix:  # get value from cmd line arg
        #         custom_results_dir_prefix = self.custom_results_dir_prefix
        #     else:
        #         custom_results_dir_prefix = ''
        results_dir_out = self.get_results_dir(results_dir,
                                               log_file,
                                               custom_results_dir_prefix,
                                               self.get_formated_timestamp(datetime.now(), timestamp_format))
        return {
            'test_regexes': {
                'class_regex': self.__prepare_regex(class_regex),
                'file_regex': self.__prepare_regex(file_regex),
                'method_regex': self.__prepare_regex(method_regex)
            },
            'formats': {
                'timestamp_format': timestamp_format
            },
            'results_dir': results_dir_out,
            'log_file': log_file
        }

    def get_results_dir(self, results_dir, logfile, custom_results_location, timestamp):
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        results_dir_timestamped = os.path.join(custom_results_location, results_dir, timestamp) \
            if custom_results_location else os.path.join(results_dir, timestamp)
        if not os.path.exists(results_dir_timestamped):
            os.makedirs(results_dir_timestamped)
        return os.path.join(results_dir_timestamped, logfile)

    def get_formated_timestamp(self, time_string, time_format):
        if '%%' in time_format:
            time_format = time_format.replace('%%', '%')
        return time_string.strftime(time_format)


config = Config().get_configuration()
