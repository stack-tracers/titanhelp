import unittest
from app import app

SHORT_TEXT = "Lorem ipsum dolor"
LONG_TEXT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut nec libero et diam vestibulum eleifend. Vivamus porta, purus sed tempor dapibus, velit mauris sodales magna, in convallis turpis nisi sed nulla. Quisque nec urna dignissim, aliquam nunc sed, molestie urna. Donec vitae ipsum ultrices, suscipit felis in, pulvinar mauris. Nullam mollis, ante eget sodales eleifend, dolor sem lacinia massa, nec porta leo leo eget felis. Nullam laoreet varius libero. Etiam a leo eget leo euismod iaculis sed et tortor. Donec nisl nibh, porta eu enim et, rutrum viverra nunc. Mauris vitae scelerisque ex. Vestibulum ex velit, malesuada in nunc ac, tristique gravida justo. Nunc non tristique risus, vitae scelerisque nibh."


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
            print(response.get_data(as_text=True))

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


        
if __name__ == '__main__':
    unittest.main()