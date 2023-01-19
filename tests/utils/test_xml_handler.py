import unittest
import xmltodict

from domain.utils.xml_handler import xml_to_dict, find_deep_value_bfs


class TestXmlToDict(unittest.TestCase):
    def test_valid_xml_string(self):
        xml_string = "<root><element>value</element></root>"
        expected_output = {"root": {"element": "value"}}
        self.assertEqual(xml_to_dict(xml_string), expected_output)

    def test_invalid_xml_string(self):
        xml_string = "invalidxmlstring"
        self.assertRaises(xmltodict.expat.ExpatError, xml_to_dict, xml_string)


class TestFindDeepValueBFS(unittest.TestCase):
    def test_find_deep_value_bfs(self):
        my_dict = {
            "level1": {
                "level2": {
                    "level3": {"deep_key": "value1"},
                    "level4": {"deep_key": "value2"}
                }
            },
            "level5": {"deep_key": "value3"}
        }
        deep_value = find_deep_value_bfs(my_dict, "deep_key")
        self.assertEqual(deep_value, "value3")

    def test_find_deep_value_bfs_not_found(self):
        my_dict = {
            "level1": {
                "level2": {
                    "level3": {"key": "value1"},
                    "level4": {"key": "value2"}
                }
            },
            "level5": {"key": "value3"}
        }
        deep_value = find_deep_value_bfs(my_dict, "deep_key")
        self.assertIsNone(deep_value)

    def test_find_deep_value_bfs_empty_dict(self):
        my_dict = {}
        deep_value = find_deep_value_bfs(my_dict, "deep_key")
        self.assertIsNone(deep_value)

    def test_find_deep_value_bfs_key_is_none(self):
        my_dict = {
            "level1": {
                "level2": {
                    "level3": {"deep_key": "value1"},
                    "level4": {"deep_key": "value2"}
                }
            },
            "level5": {"deep_key": "value3"}
        }
        deep_value = find_deep_value_bfs(my_dict, None)
        self.assertIsNone(deep_value)

    def test_find_deep_value_bfs_data_is_not_dict(self):
        my_list = [1, 2, 3, {"deep_key": "value1"}]
        deep_value = find_deep_value_bfs(my_list, "deep_key")
        self.assertIsNone(deep_value)

    def test_find_deep_value_bfs_complex_dict(self):
        my_dict = {
            "level1": {
                "level2": [
                    {"level3": {"deep_key": "value1"}},
                    {"level4": {"deep_key": "value2"}},
                    {"level5": {"level6": {"deep_key": "value3"}}}
                ]
            },
            "level7": {"deep_key": "value4"}
        }
        deep_value = find_deep_value_bfs(my_dict, "deep_key")
        self.assertEqual(deep_value, "value4")


if __name__ == "__main__":
    unittest.main()
