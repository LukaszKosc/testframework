import os
import importlib.util
import re
from glob import glob
from testframework.libraries.logger import logger


def get_test_files(file_name_regex):
    py_files = glob("./**/*.py", recursive=True)
    # exclude executor (__main__) and module file (__init__)
    src_files = [src_file for src_file in py_files if "__main__" not in src_file and "__init__" not in src_file]
    file_matcher = re.compile(file_name_regex)
    return [src_file for src_file in src_files if file_matcher.match(os.path.basename(src_file).replace('.py', ''))]


def get_test_classes(test_files, class_name_regex):
    class_matcher = re.compile(class_name_regex)
    test_classes = []
    for test_file in test_files:
        spec = importlib.util.spec_from_file_location("module.name", test_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # get all classes from modules matching regex
        test_classes.extend([(module, class_inst) for class_inst in dir(module) if class_matcher.match(class_inst)])

    return test_classes


def check_class_uniqueness(test_classes):
    test_classes_names = [item[1] for item in test_classes]
    test_classes_count = {}
    for class_name in test_classes_names:
        if class_name not in test_classes_count:
            test_classes_count[class_name] = 1
        else:
            test_classes_count[class_name] += 1
    test_class_not_unique = [class_name for class_name, class_count in test_classes_count.items() if class_count > 1]
    if test_class_not_unique:
        logger.Critical("Tests cannot be executed, not all classes are unique.")
        for class_name in test_class_not_unique:
            logger.Critical('Test class {} is not unique'.format(class_name))
        logger.Critical("Please remove ambiguous test class file and rerun tests.")
        return False
    return True


def run_tests(configuration):
    test_classes = get_test_classes(test_files=get_test_files(configuration['test_regexes']['file_regex']),
                                    class_name_regex=configuration['test_regexes']['class_regex'])
    if not test_classes:
        logger.Info('No tests found. Exiting...')
        exit(0)

    if check_class_uniqueness(test_classes):
        test_classes = sorted(test_classes, key=lambda item: item[1])

        for _class in test_classes:
            getattr(_class[0], _class[1])()
