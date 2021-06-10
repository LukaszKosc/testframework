import sys
import os
import importlib.util
from glob import glob
import importlib.util
import configparser
import re



def read_config(path_to_config=None, reversed=False):
    # reversed == True -> if you want to have deepest config file value written on top of all [previous] configs
    global_config = {}
    all_configs = []
    if not path_to_config:
        path_to_config = os.getcwd()
    config_files = glob("{}/**/*conf*.ini".format(path_to_config), recursive=True)
    config_files = sorted(config_files, reverse=reversed)
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
                    global_config[_cfg_key][k] = config['config'][_cfg_key][k]
    sorted_keys = sorted(global_config.keys())
    return {k: global_config[k] for k in sorted_keys}


def prepare_regex(in_regex):
    return '^{}$'.format(in_regex.replace('*', '.*')) \
        if any([True for char in in_regex if char in ['*', '.']]) \
        else '^{}.*$'.format(in_regex)


def get_configuration():
    class_regex = 'Test'
    method_regex = 'test_'
    file_regex = 'test_'
    config = read_config()
    if config:
        if 'class_regex' in config['GLOBAL']:
            class_regex = config['GLOBAL']['class_regex']
        if 'file_regex' in config['GLOBAL']:
            file_regex = config['GLOBAL']['file_regex']
        if 'method_regex' in config['GLOBAL']:
            method_regex = config['GLOBAL']['method_regex']
    return {'class_regex': prepare_regex(class_regex),
            'file_regex': prepare_regex(file_regex),
            'method_regex': prepare_regex(method_regex)}


def get_matcher(regex):
    return re.compile(regex)


def get_test_files(file_name_regex):
    py_files = glob("./**/*.py", recursive=True)
    # exclude executor (__main__) and module file (__init__)
    src_files = [src_file for src_file in py_files if "__main__" not in src_file and "__init__" not in src_file]
    file_matcher = get_matcher(file_name_regex)
    return [src_file for src_file in src_files if file_matcher.match(os.path.basename(src_file).replace('.py', ''))]


def run_tests(configuration):
    run_test_classes(test_files=get_test_files(configuration['file_regex']),
                     class_name_regex=configuration['class_regex'],
                     method_regex=configuration['method_regex'])


def run_test_classes(test_files, class_name_regex, method_regex):
    class_matcher = get_matcher(class_name_regex)
    
    for test_file in test_files:
        spec = importlib.util.spec_from_file_location("module.name", test_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # get all classes from modules matching regex
        test_classes = [class_inst for class_inst in dir(module) if class_matcher.match(class_inst)]

        for class_test in test_classes:
            getattr(module, class_test)()
            

run_tests(get_configuration())