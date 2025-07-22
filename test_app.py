import unittest
import json
from app import app

class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_recommendations(self):
        response = self.app.get('/api/user/recommendations')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('recommendations', data)

    def test_mcp_prompt_success(self):
        payload = {
            "mcp_server_id": "fi_money_mcp",
            "prompt_id": "investment_suggestions"
        }
        response = self.app.post('/api/mcp/prompt',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('recommendations', data)

    def test_mcp_prompt_invalid_mcp_server(self):
        payload = {
            "mcp_server_id": "invalid_mcp",
            "prompt_id": "investment_suggestions"
        }
        response = self.app.post('/api/mcp/prompt',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['error'], 'MCP server not found.')

    def test_mcp_prompt_invalid_prompt(self):
        payload = {
            "mcp_server_id": "fi_money_mcp",
            "prompt_id": "invalid_prompt"
        }
        response = self.app.post('/api/mcp/prompt',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['error'], 'Prompt not found.')

    def test_mcp_prompt_missing_params(self):
        payload = {
            "mcp_server_id": "fi_money_mcp"
        }
        response = self.app.post('/api/mcp/prompt',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['error'], 'mcp_server_id and prompt_id are required.')

if __name__ == '__main__':
    unittest.main()
