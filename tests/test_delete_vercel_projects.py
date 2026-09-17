import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from delete_vercel_projects import parse_selection, load_env, get_headers, format_date

class TestDeleteVercelProjects(unittest.TestCase):
    def setUp(self):
        self.max_index = 5
        self.projects_dict = {
            1: {"id": "prj_1", "name": "nextjs-blog", "framework": "nextjs", "updatedAt": 1690000000000},
            2: {"id": "prj_2", "name": "vite-dashboard", "framework": "vite", "updatedAt": 1690000000000},
            3: {"id": "prj_3", "name": "docs-site", "framework": "docusaurus", "updatedAt": 1690000000000},
            4: {"id": "prj_4", "name": "api-service", "framework": "express", "updatedAt": 1690000000000},
            5: {"id": "prj_5", "name": "landing-page", "framework": "html", "updatedAt": 1690000000000},
        }

    def test_parse_selection_single_digit(self):
        result = parse_selection("3", self.max_index, self.projects_dict)
        self.assertEqual(result, [3])

    def test_parse_selection_multiple_digits_comma(self):
        result = parse_selection("1, 4, 5", self.max_index, self.projects_dict)
        self.assertEqual(result, [1, 4, 5])

    def test_parse_selection_range_hyphen(self):
        result = parse_selection("2-4", self.max_index, self.projects_dict)
        self.assertEqual(result, [2, 3, 4])

    def test_parse_selection_all_keyword(self):
        result = parse_selection("all", self.max_index, self.projects_dict)
        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_parse_selection_project_name(self):
        result = parse_selection("docs-site", self.max_index, self.projects_dict)
        self.assertEqual(result, [3])

    def test_parse_selection_substring(self):
        result = parse_selection("dashboard", self.max_index, self.projects_dict)
        self.assertEqual(result, [2])

    def test_parse_selection_out_of_bounds(self):
        result = parse_selection("99", self.max_index, self.projects_dict)
        self.assertEqual(result, [])

    def test_get_headers(self):
        headers = get_headers("fake_vercel_token_123")
        self.assertEqual(headers["Authorization"], "Bearer fake_vercel_token_123")
        self.assertEqual(headers["Content-Type"], "application/json")

    def test_load_env(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, encoding="utf-8") as temp_env:
            temp_env.write("TEST_VERCEL_TOKEN=token_val_123\n")
            temp_env_path = temp_env.name

        try:
            load_env(temp_env_path)
            self.assertEqual(os.environ.get("TEST_VERCEL_TOKEN"), "token_val_123")
        finally:
            os.remove(temp_env_path)

    def test_format_date(self):
        formatted = format_date(1690000000000)
        self.assertNotEqual(formatted, "N/A")
        self.assertEqual(format_date(None), "N/A")

if __name__ == "__main__":
    unittest.main()
