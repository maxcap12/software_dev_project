from core.ship import Ship, ShipFactory


def test_ship_starts_unsunk_with_no_hits():
    ship = Ship(name="Destroyer", size=2)
    assert ship.hits == set()
    assert not ship.is_sunk


def test_ship_with_no_assigned_coordinates_is_never_sunk():
    ship = Ship(name="Destroyer", size=2)
    assert not ship.is_sunk


def test_ship_is_sunk_once_every_coordinate_is_hit():
    ship = Ship(name="Destroyer", size=2)
    ship.coordinates = [(0, 0), (1, 0)]

    ship.register_hit(0, 0)
    assert not ship.is_sunk

    ship.register_hit(1, 0)
    assert ship.is_sunk


def test_ship_factory_creates_ship_with_correct_size():
    carrier = ShipFactory.create("Carrier")
    assert carrier.name == "Carrier"
    assert carrier.size == 5


def test_ship_factory_creates_the_standard_five_ship_fleet():
    fleet = ShipFactory.create_fleet()
    assert set(fleet) == {"Carrier", "Battleship", "Cruiser", "Submarine", "Destroyer"}
    assert sum(ship.size for ship in fleet.values()) == 17
