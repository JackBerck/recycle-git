import os
import sys
import tempfile
import unittest

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from delete_repos import parse_selection, load_env, get_headers

class TestDeleteRepos(unittest.TestCase):
    def setUp(self):
        self.max_index = 10
        self.repos_dict = {
            1: {"name": "dotnet", "full_name": "user/dotnet"},
            2: {"name": "api_muntrail_go", "full_name": "user/api_muntrail_go"},
            3: {"name": "code-documentation", "full_name": "user/code-documentation"},
            4: {"name": "mrebet", "full_name": "user/mrebet"},
            5: {"name": "ionic-kuis-pemmob", "full_name": "user/ionic-kuis-pemmob"},
            6: {"name": "flutter-kuis-pemmob", "full_name": "user/flutter-kuis-pemmob"},
            7: {"name": "warasin-v2", "full_name": "user/warasin-v2"},
            8: {"name": "portfolio", "full_name": "user/portfolio"},
            9: {"name": "weatherly", "full_name": "user/weatherly"},
            10: {"name": "jackberck.github.io", "full_name": "user/jackberck.github.io"},
        }

    def test_parse_selection_single_digit(self):
        result = parse_selection("5", self.max_index, self.repos_dict)
        self.assertEqual(result, [5])

    def test_parse_selection_multiple_digits_comma(self):
        result = parse_selection("1, 3, 5", self.max_index, self.repos_dict)
        self.assertEqual(result, [1, 3, 5])

    def test_parse_selection_multiple_digits_space(self):
        result = parse_selection("1 3 5", self.max_index, self.repos_dict)
        self.assertEqual(result, [1, 3, 5])

    def test_parse_selection_range_hyphen(self):
        result = parse_selection("2-5", self.max_index, self.repos_dict)
        self.assertEqual(result, [2, 3, 4, 5])

    def test_parse_selection_range_dots(self):
        result = parse_selection("2..4", self.max_index, self.repos_dict)
        self.assertEqual(result, [2, 3, 4])

    def test_parse_selection_all_keyword(self):
        result = parse_selection("all", self.max_index, self.repos_dict)
        self.assertEqual(result, list(range(1, 11)))

    def test_parse_selection_asterisk_keyword(self):
        result = parse_selection("*", self.max_index, self.repos_dict)
        self.assertEqual(result, list(range(1, 11)))

    def test_parse_selection_repo_name(self):
        result = parse_selection("weatherly", self.max_index, self.repos_dict)
        self.assertEqual(result, [9])

    def test_parse_selection_repo_name_substring(self):
        result = parse_selection("kuis-pemmob", self.max_index, self.repos_dict)
        self.assertEqual(result, [5, 6])

    def test_parse_selection_out_of_bounds(self):
        result = parse_selection("99", self.max_index, self.repos_dict)
        self.assertEqual(result, [])

    def test_get_headers(self):
        headers = get_headers("fake_token_123")
        self.assertEqual(headers["Authorization"], "Bearer fake_token_123")
        self.assertEqual(headers["Accept"], "application/vnd.github+json")
        self.assertEqual(headers["X-GitHub-Api-Version"], "2022-11-28")

    def test_load_env(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, encoding="utf-8") as temp_env:
            temp_env.write("TEST_GITHUB_TOKEN=test_val_999\n")
            temp_env_path = temp_env.name

        try:
            load_env(temp_env_path)
            self.assertEqual(os.environ.get("TEST_GITHUB_TOKEN"), "test_val_999")
        finally:
            os.remove(temp_env_path)

if __name__ == "__main__":
    unittest.main()
