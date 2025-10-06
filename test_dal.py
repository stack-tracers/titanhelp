import re
import pytest
from pathlib import Path

from titanhelp_dal.dal import TitanHelpDAL, Ticket, STATUS_VALUES, PRIORITY_VALUES


TIMESTAMP_RX = re.compile(r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}$") 

@pytest.fixture
def db_path(tmp_path: Path) -> str:
    return str(tmp_path / "test_titanhelp.db")

@pytest.fixture
def dal(db_path: str) -> TitanHelpDAL:
   
    return TitanHelpDAL(db_path, journal_mode="DELETE", synchronous="OFF")

def make_long(n: int) -> str:
    return "x" * n

#create_ticket

def test_create_ticket_valid_returns_ticket_with_defaults(dal: TitanHelpDAL):
    t = dal.create_ticket(name="Printer is down", description="2nd lab", priority="High")
    assert isinstance(t, Ticket)
    assert t.id is not None
    assert t.name == "Printer is down"
    assert t.description == "2nd lab"
    assert t.status == "Open"
    assert t.priority == "High"
    assert t.created_at and TIMESTAMP_RX.match(t.created_at)

def test_create_ticket_applies_default_priority_low(dal: TitanHelpDAL):
    t = dal.create_ticket(name="Mouse broken", description="Comp Lab")
    assert t.priority == "Low"

@pytest.mark.parametrize("bad_name", ["", "   "])
def test_create_ticket_blank_name_raises(dal: TitanHelpDAL, bad_name):
    with pytest.raises(ValueError, match="Name is required"):
        dal.create_ticket(name=bad_name, description="desc")

@pytest.mark.parametrize("bad_desc", ["", "   "])
def test_create_ticket_blank_description_raises(dal: TitanHelpDAL, bad_desc):
    with pytest.raises(ValueError, match="Problem Description is required"):
        dal.create_ticket(name="ok", description=bad_desc)

def test_create_ticket_too_long_name_raises(dal: TitanHelpDAL):
    with pytest.raises(ValueError):
        dal.create_ticket(name=make_long(101), description="ok")

def test_create_ticket_too_long_description_raises(dal: TitanHelpDAL):
    with pytest.raises(ValueError):
        dal.create_ticket(name="ok", description=make_long(1001))

#get_ticket

def test_get_ticket_by_valid_id_returns_ticket(dal: TitanHelpDAL):
    created = dal.create_ticket("VPN", "Cannot connect")
    fetched = dal.get_ticket(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "VPN"
    assert fetched.description == "Cannot connect"

def test_get_ticket_invalid_id_returns_none(dal: TitanHelpDAL):
    assert dal.get_ticket(999999) is None


# update_ticket

def test_update_ticket_single_and_multiple_fields(dal: TitanHelpDAL):
    t = dal.create_ticket("Keyboard", "Keys missing", priority="Low")

    updated = dal.update_ticket(t.id, name="Keyboard broken")
    assert updated.name == "Keyboard broken"
    assert updated.description == "Keys missing"

    updated2 = dal.update_ticket(
        t.id,
        description="Keys missing",
        status="In Progress",
        priority="Medium",
    )
    assert updated2.description == "Keys missing"
    assert updated2.status == "In Progress"
    assert updated2.priority == "Medium"

def test_update_ticket_invalid_values_raise(dal: TitanHelpDAL):
    t = dal.create_ticket("WiFi", "Slow")
    with pytest.raises(ValueError):
        dal.update_ticket(t.id, name="")
    with pytest.raises(ValueError):
        dal.update_ticket(t.id, description=" ")
    with pytest.raises(ValueError):
        dal.update_ticket(t.id, status="Reopened")
    with pytest.raises(ValueError):
        dal.update_ticket(t.id, priority="Urgent")

def test_update_ticket_nonexistent_returns_none(dal: TitanHelpDAL):
    assert dal.update_ticket(999999, name="x") is None



#  deletticket

def test_delete_ticket_valid_then_missing(dal: TitanHelpDAL):
    t = dal.create_ticket("Monitor", "Flickers")
    assert dal.get_ticket(t.id) is not None
    assert dal.delete_ticket(t.id) is True
    assert dal.get_ticket(t.id) is None

def test_delete_ticket_nonexistent_returns_false(dal: TitanHelpDAL):
    assert dal.delete_ticket(424242) is False

# default on creation

def test_defaults_on_creation(dal: TitanHelpDAL):
    t = dal.create_ticket("Scanner", "Not detected")
    assert t.status == "Open"
    assert t.priority == "Low"
    assert t.created_at and TIMESTAMP_RX.match(t.created_at)