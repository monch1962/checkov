import os
import unittest

from checkov.common.checks_infra.checks_parser import NXGraphCheckParser
from checkov.common.checks_infra.registry import Registry
from checkov.runner_filter import RunnerFilter
from pathlib import Path
from checkov.terraform.runner import Runner, resource_registry


class TestGraphChecks(unittest.TestCase):

    def test_internal_graph_checks_load(self):
        registry = Registry(parser=NXGraphCheckParser(), checks_dir=str(
            Path(__file__).parent.parent.parent.parent / "checkov" / "terraform" / "checks" / "graph_checks"))
        registry.load_checks()
        runner_filter = RunnerFilter()
        for check in registry.checks:
            self.assertFalse(runner_filter.is_external_check(check))

    def test_external_graph_check_load(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        runner.graph_registry.checks = []
        extra_checks_dir_path = [current_dir + "/extra_yaml_checks"]
        runner.load_external_checks(extra_checks_dir_path)
        self.assertEqual(len(runner.graph_registry.checks), 1)
        runner_filter = RunnerFilter()
        for check in runner.graph_registry.checks:
            self.assertTrue(runner_filter.is_external_check(check.id))
        runner.graph_registry.checks[:] = [check for check in runner.graph_registry.checks if "CUSTOM_GRAPH_AWS_1" not
                                           in check.id]

    def test_external_checks_and_graph_checks_load(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # without external yaml checks the external graph registry checks should be 0
        extra_checks_dir_path = [current_dir + "/extra_checks"]
        runner_filter = RunnerFilter(framework='terraform')
        runner.run(root_folder=current_dir, external_checks_dir=extra_checks_dir_path,
                   runner_filter=runner_filter)
        external_graph_checks = 0
        for check in runner.graph_registry.checks:
            if runner_filter.is_external_check(check.id):
                external_graph_checks += 1
        self.assertEqual(external_graph_checks, 0)

        # with external yaml checks external graph registry checks count should be equal to the external graph checks
        extra_checks_dir_path = [current_dir + "/extra_checks", current_dir + "/extra_yaml_checks"]
        runner.run(root_folder=current_dir, external_checks_dir=extra_checks_dir_path,
                   runner_filter=runner_filter)
        for check in runner.graph_registry.checks:
            if runner_filter.is_external_check(check.id):
                external_graph_checks += 1
        self.assertTrue(len(runner.graph_registry.checks) > 1)
        self.assertEqual(external_graph_checks, 1)
        runner.graph_registry.checks[:] = [check for check in runner.graph_registry.checks if
                                           "CUSTOM_GRAPH_AWS_1" not in check.id]


if __name__ == '__main__':
    unittest.main()
