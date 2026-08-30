"""
Tests for pure functions in eval_custom.py.

Run with:
    python test_eval_functions.py
"""

import sys
import unittest

from eval_custom import (
    is_valid_json,
    classify_dataset_type,
    classify_task_type,
    check_correctness,
    compute_accuracy,
)


class TestIsValidJson(unittest.TestCase):

    def test_valid_object(self):
        self.assertTrue(is_valid_json('{"name": "foo"}'))

    def test_valid_array(self):
        self.assertTrue(is_valid_json('[{"name": "foo"}]'))

    def test_valid_empty_array(self):
        self.assertTrue(is_valid_json('[]'))

    def test_plain_text(self):
        self.assertFalse(is_valid_json("Hello, how can I help?"))

    def test_partial_json(self):
        self.assertFalse(is_valid_json('{"name": "foo"'))

    def test_empty_string(self):
        self.assertFalse(is_valid_json(""))

    def test_none(self):
        self.assertFalse(is_valid_json(None))


class TestClassifyDatasetType(unittest.TestCase):

    def test_mouse(self):
        input_text = 'tools: [{"function": {"name": "set_mouse_line"}}]'
        self.assertEqual(classify_dataset_type(input_text), "Mouse")

    def test_macaque(self):
        input_text = 'tools: [{"function": {"name": "filter_neurons_by_hemisphere"}}]'
        self.assertEqual(classify_dataset_type(input_text), "Macaque")

    def test_neuroviz(self):
        input_text = 'tools: [{"function": {"name": "render_scene"}}]'
        self.assertEqual(classify_dataset_type(input_text), "Neuroviz")

    def test_mouse_takes_priority_over_neuroviz(self):
        # if both keywords appear, Mouse should win (checked first)
        input_text = 'set_mouse_line filter_neurons_by_hemisphere'
        self.assertEqual(classify_dataset_type(input_text), "Mouse")


class TestClassifyTaskType(unittest.TestCase):

    def test_zero_plain_text(self):
        self.assertEqual(classify_task_type("Hello, I can help you."), "Zero")

    def test_zero_empty_array(self):
        self.assertEqual(classify_task_type("[]"), "Zero")

    def test_single_object(self):
        target = '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Thy1-YFP"}}]'
        self.assertEqual(classify_task_type(target), "Single")

    def test_single_bare_object(self):
        # non-list JSON object also counts as Single
        target = '{"name": "set_mouse_line", "arguments": {"mouse_line": "Thy1-YFP"}}'
        self.assertEqual(classify_task_type(target), "Single")

    def test_parallel(self):
        target = (
            '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Orexin"}}, '
            '{"name": "query_neurons_by_structure", "arguments": {"axon_only": true}}]'
        )
        self.assertEqual(classify_task_type(target), "Parallel")


class TestCheckCorrectness(unittest.TestCase):

    # ── Zero task ────────────────────────────────────────────────────────────

    def test_zero_correct_plain_text(self):
        self.assertTrue(check_correctness("Hello!", "Hello world", "Zero"))

    def test_zero_incorrect_returns_json(self):
        self.assertFalse(check_correctness('[{"name": "foo"}]', "Hello world", "Zero"))

    # ── Single task ──────────────────────────────────────────────────────────

    def test_single_exact_match(self):
        target = '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Thy1-YFP"}}]'
        pred   = '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Thy1-YFP"}}]'
        self.assertTrue(check_correctness(pred, target, "Single"))

    def test_single_whitespace_difference(self):
        target = '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Thy1-YFP"}}]'
        pred   = '[  { "name" :  "set_mouse_line" , "arguments" : { "mouse_line" : "Thy1-YFP" } }  ]'
        self.assertTrue(check_correctness(pred, target, "Single"))

    def test_single_wrong_value(self):
        target = '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Thy1-YFP"}}]'
        pred   = '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Orexin"}}]'
        self.assertFalse(check_correctness(pred, target, "Single"))

    def test_single_pred_not_json(self):
        target = '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Thy1-YFP"}}]'
        self.assertFalse(check_correctness("not json", target, "Single"))

    def test_single_array_wrapping_mismatch_target_wrapped(self):
        # target is array with 1 element, pred is bare object
        target = '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Thy1-YFP"}}]'
        pred   = '{"name": "set_mouse_line", "arguments": {"mouse_line": "Thy1-YFP"}}'
        self.assertTrue(check_correctness(pred, target, "Single"))

    def test_single_array_wrapping_mismatch_pred_wrapped(self):
        # target is bare object, pred is array with 1 element
        target = '{"name": "set_mouse_line", "arguments": {"mouse_line": "Thy1-YFP"}}'
        pred   = '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Thy1-YFP"}}]'
        self.assertTrue(check_correctness(pred, target, "Single"))

    # ── Parallel task ────────────────────────────────────────────────────────

    def test_parallel_exact_match(self):
        target = (
            '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Orexin"}}, '
            '{"name": "query_neurons_by_structure", "arguments": {"axon_only": true}}]'
        )
        pred = (
            '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Orexin"}}, '
            '{"name": "query_neurons_by_structure", "arguments": {"axon_only": true}}]'
        )
        self.assertTrue(check_correctness(pred, target, "Parallel"))

    def test_parallel_wrong_order(self):
        target = (
            '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Orexin"}}, '
            '{"name": "query_neurons_by_structure", "arguments": {"axon_only": true}}]'
        )
        pred = (
            '[{"name": "query_neurons_by_structure", "arguments": {"axon_only": true}}, '
            '{"name": "set_mouse_line", "arguments": {"mouse_line": "Orexin"}}]'
        )
        self.assertFalse(check_correctness(pred, target, "Parallel"))

    def test_parallel_missing_one_call(self):
        target = (
            '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Orexin"}}, '
            '{"name": "query_neurons_by_structure", "arguments": {"axon_only": true}}]'
        )
        pred = '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Orexin"}}]'
        self.assertFalse(check_correctness(pred, target, "Parallel"))


class TestComputeAccuracy(unittest.TestCase):
    """
    Use a tiny mock dataset (3 samples) to verify aggregation arithmetic.
    """

    # Shared mock data: Mouse/Single correct, Macaque/Zero correct, Neuroviz/Parallel wrong
    INSTRUCTIONS = ["inst_0", "inst_1", "inst_2"]
    INPUTS = [
        'tools: [{"function": {"name": "set_mouse_line"}}]',
        'tools: [{"function": {"name": "filter_neurons_by_hemisphere"}}]',
        'tools: [{"function": {"name": "render_scene"}}]',
    ]
    TARGETS = [
        '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Thy1-YFP"}}]',  # Single
        "Hello, I can help.",                                                        # Zero
        '[{"name": "a"}, {"name": "b"}]',                                           # Parallel
    ]
    PREDICTIONS_ALL_CORRECT = [
        '[{"name": "set_mouse_line", "arguments": {"mouse_line": "Thy1-YFP"}}]',
        "Some plain text response",
        '[{"name": "a"}, {"name": "b"}]',
    ]
    PREDICTIONS_ALL_WRONG = [
        '[{"name": "set_mouse_line", "arguments": {"mouse_line": "WRONG"}}]',
        '[{"name": "oops_json"}]',   # Zero task but returned JSON → wrong
        '[{"name": "a"}]',           # Missing second call
    ]

    def test_all_correct_overall_accuracy(self):
        result = compute_accuracy(
            self.PREDICTIONS_ALL_CORRECT,
            self.TARGETS,
            self.INSTRUCTIONS,
            self.INPUTS,
        )
        self.assertEqual(result["results"]["Overall"]["correct"], 3)
        self.assertEqual(result["results"]["Overall"]["total"], 3)
        self.assertAlmostEqual(result["results"]["Overall"]["accuracy"], 1.0)

    def test_all_wrong_overall_accuracy(self):
        result = compute_accuracy(
            self.PREDICTIONS_ALL_WRONG,
            self.TARGETS,
            self.INSTRUCTIONS,
            self.INPUTS,
        )
        self.assertEqual(result["results"]["Overall"]["correct"], 0)
        self.assertEqual(result["results"]["Overall"]["total"], 3)
        self.assertAlmostEqual(result["results"]["Overall"]["accuracy"], 0.0)

    def test_correct_dimension_routing(self):
        result = compute_accuracy(
            self.PREDICTIONS_ALL_CORRECT,
            self.TARGETS,
            self.INSTRUCTIONS,
            self.INPUTS,
        )
        # Mouse/Single: 1 correct out of 1
        self.assertEqual(result["results"]["Mouse_Single"]["correct"], 1)
        self.assertEqual(result["results"]["Mouse_Single"]["total"], 1)
        # Macaque/Zero: 1 correct out of 1
        self.assertEqual(result["results"]["Macaque_Zero"]["correct"], 1)
        self.assertEqual(result["results"]["Macaque_Zero"]["total"], 1)
        # Neuroviz/Parallel: 1 correct out of 1
        self.assertEqual(result["results"]["Neuroviz_Parallel"]["correct"], 1)
        self.assertEqual(result["results"]["Neuroviz_Parallel"]["total"], 1)

    def test_details_length_matches_dataset(self):
        result = compute_accuracy(
            self.PREDICTIONS_ALL_CORRECT,
            self.TARGETS,
            self.INSTRUCTIONS,
            self.INPUTS,
        )
        self.assertEqual(len(result["details"]), 3)

    def test_details_fields_present(self):
        result = compute_accuracy(
            self.PREDICTIONS_ALL_CORRECT,
            self.TARGETS,
            self.INSTRUCTIONS,
            self.INPUTS,
        )
        detail = result["details"][0]
        for key in ("index", "instruction", "target", "prediction", "dataset_type", "task_type", "is_correct"):
            self.assertIn(key, detail)

    def test_empty_dimension_returns_zero_accuracy(self):
        result = compute_accuracy(
            self.PREDICTIONS_ALL_CORRECT,
            self.TARGETS,
            self.INSTRUCTIONS,
            self.INPUTS,
        )
        # Mouse/Zero has no samples → accuracy should be 0.0
        self.assertEqual(result["results"]["Mouse_Zero"]["total"], 0)
        self.assertAlmostEqual(result["results"]["Mouse_Zero"]["accuracy"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
