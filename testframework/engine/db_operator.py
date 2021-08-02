import atexit
import os
import sqlite3
from datetime import datetime
from sqlite3 import Error
from sqlalchemy import create_engine, Column, Date, func, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import text
Base = declarative_base()


class TestCase(Base):
    __tablename__ = 'testcase'

    id = Column(Integer, primary_key=True)
    tests_category = Column(String)
    module_name = Column(String)
    test_suite_name = Column(String, unique=True)
    test_case_names = Column(String)
    module_path = Column(String)
    run_path = Column(String)
    created = Column(String)
    updated = Column(String)
    execution_id = Column(Integer, ForeignKey("execution.id"))
    executions = relationship("Execution", foreign_keys=[execution_id])

    def __init__(self, tests_category, module_name, test_suite_name, test_case_names, module_path,
                 run_path, created):
        self.tests_category = tests_category
        self.module_name = module_name
        self.test_suite_name = test_suite_name
        self.test_case_names = test_case_names
        self.module_path = module_path
        self.run_path = run_path
        self.created = created
        self.updated = self.created

    def __repr__(self):
        ...
        return "<TestCase(id='%s', tests_category='%s', module_name='%s', test_suite_name='%s', " \
               "test_case_names='%s', module_path='%s', run_path='%s', created='%s', updated='%s')>" % (
               self.id, self.tests_category, self.module_name, self.test_suite_name,
               self.test_case_names, self.module_path, self.run_path, self.created, self.updated)

    def fields(self):
        fields = [field for field in self.__dict__ if not field.startswith('_')]
        return fields

    @staticmethod
    def excluded_fields():
        excluded_fields = ['id', 'created', 'updated', 'execution_id']
        return excluded_fields

    def get_field(self, field_name):
        return getattr(self, field_name)


class Execution(Base):
    __tablename__ = 'execution'

    id = Column(Integer, primary_key=True)
    execution_number = Column(String)
    execution_date = Column(String)
    execution_time = Column(String)

    def __init__(self, execution_date, execution_time):
        self.execution_number = -1
        self.execution_date = execution_date
        self.execution_time = execution_time

    def __repr__(self):
        return "<Execution(execution_number='%s', execution_date='%s', execution_time='%s')>" % (
            self.execution_number, self.execution_date, self.execution_time)


class Db_Operator:
    def __init__(self, configuration):
        table_objects = []
        self.db_file = 'D:\\Projects\\RemoteConnection\\tc.db'
        self.engine = create_engine("sqlite+pysqlite:///{}".format(self.db_file), echo=False, future=True)
        Base.metadata.create_all(self.engine, tables=table_objects)
        self._config = configuration
        self.session = Session(self.engine, future=True)

        TestCase.__table__.create(self.engine, checkfirst=True)
        Execution.__table__.create(self.engine, checkfirst=True)
        # TestCase.__table__.drop(self.engine)
        # Execution.__table__.drop(self.engine)
        atexit.register(self.close_connection)

    def insert_record(self, values):
        new_test_case = TestCase(
            tests_category=values['tests_category'],
            module_name=values['module_name'],
            test_suite_name=values['test_suite_name'],
            test_case_names=values['test_case_names'],
            module_path=values['module_path'],
            run_path=values['run_path'],
            created=0
        )
        # results = self.session.query(TestCase).filter_by(
        #     tests_category=values['tests_category'],
        #     module_name=values['module_name'],
        #     test_suite_name=values['test_suite_name'],
        #     test_case_names=values['test_case_names'],
        #     module_path=values['module_path'],
        #     created=0).all()

        result = self.session.query(TestCase).filter_by(
            tests_category=values['tests_category'],
            module_name=values['module_name'],
            test_suite_name=values['test_suite_name']).all()
        if not result:
            self.session.add(new_test_case)
        self.session.commit()

    def is_record_present(self, values):
        test_case = self.session.query(TestCase).filter_by(test_suite_name=values['test_suite_name']).all()
        length = len(test_case)
        return True if length >= 1 else False

    def is_record_equal(self, record, values, fields_to_ignore=None):
        check_fields = list(set(record.fields()) - set(TestCase.excluded_fields()))
        if fields_to_ignore:
            check_fields = list(set(check_fields) - set(fields_to_ignore))
        equal = 0
        for field in check_fields:
            if isinstance(values, dict):
                if record.get_field(field) == values[field]:
                    equal += 1
            if isinstance(values, TestCase):
                if record.get_field(field) == values.get_field(field):
                    equal += 1
        if equal == len(check_fields):
            return True
        return False

    def delete_non_existing_test(self, result):
        for record_index in range(0, len(result)):
            if not os.path.exists(result[record_index].module_path):
                non_existing_test = self.session.query(TestCase).filter_by(id=result[record_index].id)[0]
                self.session.delete(non_existing_test)
                self.session.commit()

    def is_record_duplicated(self, test_suite_name):
        result = self.session.query(TestCase).filter_by(test_suite_name=test_suite_name).all()
        length = len(result)
        if length == 1:
            return False
        if length > 1:
            return True

    def retrieve_record(self, test_suite_name):
        if self.is_record_present({'test_suite_name': test_suite_name}):
            result = self.session.query(TestCase).filter_by(test_suite_name=test_suite_name).all()
            length = len(result)
            if length > 1:
                self.delete_non_existing_test(result)
            elif length == 1:
                return result[0]
        return None

    def retrieve_tests(self, where_filter):
        where_filter = where_filter.replace(' %', ' "%')
        where_filter = where_filter.replace('% ', '%" ')
        where_filter = where_filter.replace('%;', '%";')
        result = self.session.execute(text(where_filter)).all()
        result = [item[0] for item in result]
        return result

    def update_record(self, record, updated_values):
        test_case_query = self.session.query(TestCase).filter_by(id=record.get_field('id'))
        # test_case_query = self.session.query(TestCase).filter_by(id=100)
        count = self.session.query(func.count('*')).select_from(test_case_query).scalar()
        if count:
            test_case = test_case_query[0]
        check_fields = list(set(record.fields()) - set(TestCase.excluded_fields()))

        for field in check_fields:
            setattr(test_case, str(field), updated_values[field])

        time_format = self._config['formats']['timestamp_format']
        if '%%' in time_format:
            time_format = time_format.replace('%%', '%')
        updated_value = datetime.now().strftime(time_format)
        setattr(test_case, 'updated', updated_value)
        self.session.commit()

    def close_connection(self):
        print('disconnecting')
        if self.session:
            self.session.close()
        # self.engine.dispose()
