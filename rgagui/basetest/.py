import time
import logging

from . import BaseTest, FloatInput


class BasePassFailTest(BaseTest):
    TimeoutPeriod = 'Timeout period'

    input_parameters = {
        TimeoutPeriod: FloatInput(60.0, " s", 1.0, 1200.0, 1.0)
    }

    TestQuestions = [
        'This is the first question'
    ]

    def setup(self):
        self.logger = self.get_logger(__name__)

        self.timeout_period = self.input_parameters[self.TimeoutPeriod].value

    def test(self):
        test_passed = True
        table_name = 'Pass/fail test'
        self.create_table(table_name, 'Test', 'Result')
        for index, question in enumerate(self.TestQuestions):
            if not self.is_running():
                break
            self.prepare_questions(index)
            result = self.ask_question(question, timeout=self.timeout_period)
            # result = self.get_answer()
            result_string = 'Aborted' if result is None else \
                            'Pass' if result is True else \
                            '** FAIL **'
            self.logger.info('Test result: {}'.format(result_string))
            if result is None:
                self.stop()
                test_passed = False
                break
            else:
                test_passed = test_passed and result
                self.display_result("'{}': {}".format(question, result_string))
                self.add_data_to_table(table_name, question, result_string)
        self.set_test_passed(test_passed)

    def cleanup(self):
        pass

    def prepare_questions(self, index):
        """Add action to be done before a question"""
        if index >= len(self.TestQuestions):
            self.logger.error('Index {} is out of range'.format(index))
        if index == 0:
            self.logger.debug("Test '{}' is prepared".format(self.TestQuestions[index]))
        elif index == 1:
            self.logger.debug("Test '{}' is prepared".format(self.TestQuestions[index]))
        else:
            self.logger.debug("Test '{}' is prepared".format(self.TestQuestions[index]))

