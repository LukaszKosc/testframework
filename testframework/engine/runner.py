import ast
import importlib.util
from inspect import getmembers, isfunction

import os
import re

from glob import glob
from testframework.libraries.logger import logger
from testframework.engine.db_operator import Db_Operator, TestCase

def scan_test_folder_for_test_files(file_name_regex):
    py_files = glob("./**/*.py", recursive=True)
    # exclude executor (__main__) and module file (__init__)
    src_files = [src_file for src_file in py_files if "__main__" not in src_file and "__init__" not in src_file]
    file_matcher = re.compile(file_name_regex)
    return [src_file for src_file in src_files if file_matcher.match(os.path.basename(src_file).replace('.py', ''))]


def get_class_info(class_item):
    module_info = str(class_item[0]).split()
    module_name = module_info[1].strip('\'')
    test_suite_name = class_item[1]
    test_case_names = ','.join(class_item[2])
    module_path = get_module_path(class_item[0])
    run_path='{}{}'.format('.{0}testframework{0}'.format(os.path.sep), module_path.split('{0}testframework{0}'.format(os.path.sep))[1])
    tests_category = module_path.split('{0}tests{0}'.format(os.path.sep))[1].split('{}'.format(os.path.sep))
    tests_category = tests_category[0] if len(tests_category) >= 2 else ''
    return {'tests_category': tests_category,
            'module_name': module_name,
            'test_suite_name': test_suite_name,
            'test_case_names': test_case_names,
            'module_path': module_path,
            'run_path': run_path}


def gather_duplicated_classes(test_classes, duplicated_classes):
    logger.Critical("Tests cannot be executed, not all classes are unique.")
    duplicated_classes_details = {}
    for class_item in test_classes:
        class_info = get_class_info(class_item)
        if class_info['test_suite_name'] in duplicated_classes:
            if class_info['test_suite_name'] not in duplicated_classes_details:
                duplicated_classes_details[class_info['test_suite_name']]={'paths': [class_info['module_path']]}
            else:
                duplicated_classes_details[class_info['test_suite_name']]['paths'].append(class_info['module_path'])

    return duplicated_classes_details

def log_duplicated_classes(duplicated_classes):
    for class_name, paths_list in duplicated_classes.items():
        single_class_paths_list = '"{}" is present in following files:'.format(class_name) + \
                                  ''.join(['\n\t * {}'.format(path) for paths in paths_list.values() for path in paths ])
        logger.Critical(single_class_paths_list)


def are_classes_unique(test_classes_to_check):
    test_classes_names = [item[1] for item in test_classes_to_check]
    test_classes_names_unique = set(test_classes_names)
    if len(test_classes_names) > len(test_classes_names_unique):
        duplicated_classes_unique = \
            list(set([name for name in test_classes_names if test_classes_names.count(name) > 1]))
        log_duplicated_classes(gather_duplicated_classes(test_classes_to_check, duplicated_classes_unique))
        return False
    return True


def sort_test_classes(classes):
    return sorted(classes, key=lambda item: item[1])  #, reverse=True)


def verify_if_tests_are_categorized(test_classes, mandatory_category=True):
    if not mandatory_category:
        return sort_test_classes(test_classes)
    tests = []
    for _class in test_classes:
        class_full_info = get_class_info(_class)
        if class_full_info['tests_category'] != '':
            tests.append(_class)
        else:
            logger.Info('If test "{}" ({}) is supposed to be executed it should be moved into folder (category).'.format(class_full_info['test_suite_name'], class_full_info['module_path']))
    return sort_test_classes(tests)


def get_module_path(module_header):
    module_header = str(module_header).strip('<>')
    module_header = module_header.replace('{0}{0}.'.format(os.path.sep), '') \
        if '{0}{0}.'.format(os.path.sep) in module_header else module_header
    module_header = module_header.replace('{0}{0}'.format(os.path.sep), '{0}'.format(os.path.sep)) \
        if '{0}{0}'.format(os.path.sep) in module_header else module_header
    module_path = module_header.split()[3]
    module_path = module_path.replace('{0}{0}'.format(os.path.sep), '{0}'.format(os.path.sep)) \
        if '{0}{0}'.format(os.path.sep) in module_path else module_path
    return module_path.replace('\'', '')


def get_methods(test_file, class_name):
    methods = []
    with open(test_file, 'r') as source_file:
        source = source_file.read()
        for f in ast.parse(source).body:
            if isinstance(f, ast.ClassDef) and class_name == f.name:
                for node in ast.walk(f):
                    if isinstance(node, ast.FunctionDef):
                        methods.append(node.name)
    return methods


def get_classes(configuration, test_files=None):
    test_files = test_files if test_files else scan_test_folder_for_test_files(configuration['test_regexes']['file_regex'].lower())
    class_matcher = re.compile(configuration['test_regexes']['class_regex'].lower())
    method_matcher = re.compile(configuration['test_regexes']['method_regex'].lower())
    return inspect_test_files_for_classes_and_methods(test_files, class_matcher, method_matcher)


def inspect_test_files_for_classes_and_methods(test_files, class_matcher, method_matcher):  # , class_name_regex=None, method_name_regex=None):
    test_classes = []
    for test_file in test_files:
        module_name_file_path_based = os.path.basename(test_file).strip('.py').replace('_', ' ').title().replace(' ', '')
        spec = importlib.util.spec_from_file_location(module_name_file_path_based, test_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # not running tests without this line
        # get all classes from modules matching regex
        for class_inst in dir(module):
            if class_matcher.match(class_inst.lower()):
                test_methods = [method for method in get_methods(test_file, class_inst) if method_matcher.match(method.lower())]
                test_classes.append((module, class_inst, test_methods))
    return test_classes


def register_tests(test_classes, db):
    created, updated = 0, 0
    for class_item in test_classes:
        class_item_info = get_class_info(class_item)
        if db.is_record_present(class_item_info):
            if not db.is_record_duplicated(class_item_info['test_suite_name']):
                existing_record = db.retrieve_record(class_item_info['test_suite_name'])
                if existing_record:
                    if not db.is_record_equal(existing_record, class_item_info):
                        db.update_record(existing_record, class_item_info)
                        updated += 1
        else:
            db.insert_record(class_item_info)
            created += 1
    logger.Debug('Tests statistics:\ncreated: {}, updated: {}'.format(created, updated))


def filter_tests(db, filter=None):
    return db.retrieve_tests('select run_path from testcase where {};'.format(filter) if filter else 'select run_path from testcase;')
    # db.retrieve_tests('select run_path from testcase where test_suite_name like %4%;')


def run_tests(configuration, filter=None):
    test_classes = get_classes(configuration)
    if are_classes_unique(test_classes):
        if not test_classes:
            logger.Info('No tests found. Exiting...')
            exit(0)

        db = Db_Operator(configuration)
        test_classes = verify_if_tests_are_categorized(test_classes)
        register_tests(test_classes, db)

        # actual running tests - here you can use filter for test cases
        # get those test classes and paths which should be executed
        tests_from_db = filter_tests(db, filter)
        if filter and not tests_from_db:
            logger.Info('Found none tests matching filter. Exiting...')
            exit(0)
        else:
            test_classes = get_classes(configuration, tests_from_db)

        for _class in test_classes:
            getattr(_class[0], _class[1])()
