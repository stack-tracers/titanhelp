import unittest
from app import app, dal
import json

with open ("tests/test_data.json") as f:
    d = json.load(f)
    SHORT_TEXT = d["SHORT_TEXT"]
    LONG_TEXT = d["LONG_TEXT"]
    EXTREME_TEXT = d["EXTREME_TEXT"]

class TestTickets(unittest.TestCase):
    
    def test_home(self):
        with app.test_client() as c:
            response = c.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn("<h1>Tickets</h1>", response.get_data(as_text=True))

    def test_new_tickets_page(self):
        with app.test_client() as c:
            response = c.get("/new-ticket")
            self.assertEqual(response.status_code, 200)
            self.assertIn("<h1>New Ticket</h1>", response.get_data(as_text=True))

    def test_new_ticket_full_form(self):
        with app.test_client() as c:
            response = c.post("/new-ticket", data={"name":SHORT_TEXT, "description":LONG_TEXT})
            self.assertEqual(response.status_code, 201)
            self.assertIn(">Successfully Created Ticket</div>", response.get_data(as_text=True))

    def test_new_ticket_name_too_long(self):
        with app.test_client() as c:
            response = c.post("/new-ticket", data={"name":EXTREME_TEXT, "description":LONG_TEXT})
            self.assertEqual(response.status_code, 400)
            self.assertIn(">400 Length of name must be 100 words or under.</div>", response.get_data(as_text=True))

    def test_new_ticket_description_too_long(self):
        with app.test_client() as c:
            response = c.post("/new-ticket", data={"name":SHORT_TEXT, "description":EXTREME_TEXT})
            self.assertEqual(response.status_code, 400)
            self.assertIn(">400 Length of description must be 1000 words or under.</div>", response.get_data(as_text=True))

    def test_new_ticket_no_name(self):
        with app.test_client() as c:
            response = c.post("/new-ticket", data={"name":SHORT_TEXT})
            self.assertEqual(response.status_code, 400)
            self.assertIn(">400 Name and description are required.</div>", response.get_data(as_text=True))

    def test_new_ticket_no_description(self):
        with app.test_client() as c:
            response = c.post("/new-ticket", data={"description":LONG_TEXT, "description":LONG_TEXT})
            self.assertEqual(response.status_code, 400)
            self.assertIn(">400 Name and description are required.</div>", response.get_data(as_text=True))

    def test_new_ticket_wrong_priority(self):
        with app.test_client() as c:
            response = c.post("/new-ticket", data={"name":"Ceiling Fan Exploded", "description":"Please come fix this ceiling fan, it's very important!","priority":"Important"})
            self.assertEqual(response.status_code, 400)
            self.assertIn("400 ValueError: Priority must be one of", response.get_data(as_text=True))

    def test_new_ticket_correct_priority(self):
        with app.test_client() as c:
            response = c.post("/new-ticket", data={"name":"Low Priority Ticket", "description":"This is a low priority ticket","priority":'Low'}) # the priority must have apostrophes to match the db
            self.assertEqual(response.status_code, 201)
            self.assertIn(">Successfully Created Ticket</div>", response.get_data(as_text=True))

            response = c.post("/new-ticket", data={"name":"Medium Priority Ticket", "description":"This is a medium priority ticket","priority":'Medium'}) # the priority must have apostrophes to match the db
            self.assertEqual(response.status_code, 201)
            self.assertIn(">Successfully Created Ticket</div>", response.get_data(as_text=True))

            response = c.post("/new-ticket", data={"name":"High Priority Ticket", "description":"This is a high priority ticket","priority":'High'}) # the priority must have apostrophes to match the db
            self.assertEqual(response.status_code, 201)
            self.assertIn(">Successfully Created Ticket</div>", response.get_data(as_text=True))
    
    def test_closing_tickets(self):
        with app.test_client() as c:
            response = c.post("/new-ticket", data={"name":"Closed Ticket", "description":"This is a closed ticket","priority":'High'}) # the priority must have apostrophes to match the db
            self.assertEqual(response.status_code, 201)
            for t in dal.list_tickets():
                if t.name == "Closed Ticket" and t.status == "Open":
                    response = c.post(f"/ticket/{t.id}/close")
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(">Ticket has been successfully closed</div>", response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()