import unittest
import parse

class TestParse(unittest.TestCase):

    def test_parse_request(self):
        fp = open('request.txt', 'r')
        data = fp.read()
        print data

        http_request = parse.parse_request_header(data)
        print http_request
        print http_request.render()

    def test_parse_response(self):
        fp = open('response.txt', 'r')
        data = fp.read()
        print data

        http_response = parse.parse_response_header(data)
        print http_response.render()


if __name__ == "__main__":
    unittest.main()