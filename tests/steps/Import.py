from behave import *
import genre_classifier.data_preprocessing as dp
use_step_matcher("re")


@when(
    'we want to extract feature vector from first 60 seconds from data in "data/test_files"')
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    context.result = dp.import_from_dir("data/test_files", []

@then("we expect to get vectors of length 44100 \* 60 \+ 1")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    length = 44100 * 60 * 1

@step("we expect to get mapping of genres to discrete numbers")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    pass