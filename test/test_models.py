import pytest
from src.data.models import Client, Airline, Flight, create_record_from_dict, validate_record


class TestClientModel:
    """Test cases for Client model"""

    def test_client_creation(self):
        """Test basic client creation"""
        client = Client(
            ID=1,
            Name="John Doe",
            PhoneNumber="555-1234",
            Address1="123 Main St",
            City="New York",
            State="NY",
            ZipCode="10001",
            Country="USA"
        )

        assert client.ID == 1
        assert client.Type == "client"
        assert client.Name == "John Doe"
        assert client.PhoneNumber == "555-1234"
        assert client.City == "New York"

    def test_client_to_dict(self):
        """Test conversion to dictionary with frontend field names"""
        client = Client(
            ID=1,
            Name="John Doe",
            PhoneNumber="555-1234",
            City="New York"
        )

        result = client.to_dict()

        assert result['ID'] == 1
        assert result['Type'] == 'client'
        assert result['Name'] == 'John Doe'
        assert result['Phone Number'] == '555-1234'
        assert result['City'] == 'New York'
        # Check that all frontend field names are present
        expected_fields = [
            'ID', 'Type', 'Name', 'Phone Number', 'Address Line 1',
            'Address Line 2', 'Address Line 3', 'City', 'State',
            'Zip Code', 'Country'
        ]
        for field in expected_fields:
            assert field in result

    def test_client_from_frontend_dict(self):
        """Test creation from frontend dictionary format"""
        frontend_data = {
            'ID': 1,
            'Name': 'John Doe',
            'Phone Number': '555-1234',
            'City': 'New York',
            'State': 'NY',
            'Zip Code': '10001',
            'Country': 'USA'
        }

        client = Client.from_frontend_dict(frontend_data)

        assert client.ID == 1
        assert client.Name == 'John Doe'
        assert client.PhoneNumber == '555-1234'
        assert client.City == 'New York'

    def test_client_validation_success(self):
        """Test successful validation"""
        client = Client(
            ID=1,
            Name="John Doe",
            PhoneNumber="555-1234",
            City="New York",
            Country="USA"
        )

        # Should not raise any exception
        client.validate()

    def test_client_validation_missing_name(self):
        """Test validation with missing name"""
        client = Client(
            ID=1,
            Name="",  # Empty name
            PhoneNumber="555-1234",
            City="New York",
            Country="USA"
        )

        with pytest.raises(ValueError, match="Client name is required"):
            client.validate()

    def test_client_validation_missing_phone(self):
        """Test validation with missing phone number"""
        client = Client(
            ID=1,
            Name="John Doe",
            PhoneNumber="",  # Empty phone
            City="New York",
            Country="USA"
        )

        with pytest.raises(ValueError, match="Phone number is required"):
            client.validate()

    def test_client_validation_invalid_id(self):
        """Test validation with invalid ID"""
        client = Client(
            ID="invalid",  # String instead of int
            Name="John Doe",
            PhoneNumber="555-1234",
            City="New York",
            Country="USA"
        )

        # Should convert to int in post_init
        assert isinstance(client.ID, int)

    def test_client_type_fixed(self):
        """Test that Type is always 'client' regardless of input"""
        client = Client(ID=1, Name="Test", Type="invalid_type")
        assert client.Type == "client"  # Should be forced to 'client'


class TestAirlineModel:
    """Test cases for Airline model"""

    def test_airline_creation(self):
        """Test basic airline creation"""
        airline = Airline(
            ID=1,
            CompanyName="Delta Airlines"
        )

        assert airline.ID == 1
        assert airline.Type == "airline"
        assert airline.CompanyName == "Delta Airlines"

    def test_airline_to_dict(self):
        """Test conversion to dictionary"""
        airline = Airline(ID=1, CompanyName="Delta Airlines")

        result = airline.to_dict()

        assert result['ID'] == 1
        assert result['Type'] == 'airline'
        assert result['Company Name'] == 'Delta Airlines'

    def test_airline_from_frontend_dict(self):
        """Test creation from frontend dictionary format"""
        frontend_data = {
            'ID': 1,
            'Company Name': 'Delta Airlines'
        }

        airline = Airline.from_frontend_dict(frontend_data)

        assert airline.ID == 1
        assert airline.CompanyName == 'Delta Airlines'

    def test_airline_validation_success(self):
        """Test successful validation"""
        airline = Airline(ID=1, CompanyName="Delta Airlines")
        airline.validate()  # Should not raise

    def test_airline_validation_missing_company_name(self):
        """Test validation with missing company name"""
        airline = Airline(ID=1, CompanyName="")

        with pytest.raises(ValueError, match="Company name is required"):
            airline.validate()

    def test_airline_type_fixed(self):
        """Test that Type is always 'airline'"""
        airline = Airline(ID=1, CompanyName="Test", Type="invalid")
        assert airline.Type == "airline"


class TestFlightModel:
    """Test cases for Flight model"""

    def test_flight_creation(self):
        """Test basic flight creation"""
        flight = Flight(
            ID=1,
            Client_ID=101,
            Airline_ID=201,
            Date="2024-12-15T14:30:00",
            StartCity="New York",
            EndCity="London"
        )

        assert flight.ID == 1
        assert flight.Type == "flight"
        assert flight.Client_ID == 101
        assert flight.Airline_ID == 201
        assert flight.StartCity == "New York"
        assert flight.EndCity == "London"

    def test_flight_to_dict(self):
        """Test conversion to dictionary"""
        flight = Flight(
            ID=1,
            Client_ID=101,
            Airline_ID=201,
            Date="2024-12-15T14:30:00",
            StartCity="New York",
            EndCity="London"
        )

        result = flight.to_dict()

        assert result['ID'] == 1
        assert result['Type'] == 'flight'
        assert result['Client_ID'] == 101
        assert result['Airline_ID'] == 201
        assert result['Start City'] == 'New York'
        assert result['End City'] == 'London'

    def test_flight_from_frontend_dict(self):
        """Test creation from frontend dictionary format"""
        frontend_data = {
            'ID': 1,
            'Client_ID': 101,
            'Airline_ID': 201,
            'Date': '2024-12-15T14:30:00',
            'Start City': 'New York',
            'End City': 'London'
        }

        flight = Flight.from_frontend_dict(frontend_data)

        assert flight.ID == 1
        assert flight.Client_ID == 101
        assert flight.Airline_ID == 201
        assert flight.StartCity == 'New York'
        assert flight.EndCity == 'London'

    def test_flight_validation_success(self):
        """Test successful validation"""
        flight = Flight(
            ID=1,
            Client_ID=101,
            Airline_ID=201,
            Date="2024-12-15T14:30:00",
            StartCity="New York",
            EndCity="London"
        )

        flight.validate()  # Should not raise

    def test_flight_validation_invalid_date(self):
        """Test validation with invalid date"""
        flight = Flight(
            ID=1,
            Client_ID=101,
            Airline_ID=201,
            Date="invalid-date",
            StartCity="New York",
            EndCity="London"
        )

        with pytest.raises(ValueError, match="Invalid date format"):
            flight.validate()

    def test_flight_validation_missing_cities(self):
        """Test validation with missing cities"""
        flight = Flight(
            ID=1,
            Client_ID=101,
            Airline_ID=201,
            Date="2024-12-15T14:30:00",
            StartCity="",  # Empty
            EndCity="London"
        )

        with pytest.raises(ValueError, match="Start city is required"):
            flight.validate()

    def test_flight_validation_invalid_client_id(self):
        """Test validation with invalid client ID"""
        flight = Flight(
            ID=1,
            Client_ID=0,  # Invalid (should be positive)
            Airline_ID=201,
            Date="2024-12-15T14:30:00",
            StartCity="New York",
            EndCity="London"
        )

        with pytest.raises(ValueError, match="Client ID must be positive integer"):
            flight.validate()

    def test_flight_type_fixed(self):
        """Test that Type is always 'flight'"""
        flight = Flight(
            ID=1,
            Client_ID=101,
            Airline_ID=201,
            Date="2024-12-15",
            StartCity="A",
            EndCity="B",
            Type="invalid"
        )
        assert flight.Type == "flight"


class TestFactoryFunctions:
    """Test cases for factory functions"""

    def test_create_record_from_dict_client(self):
        """Test creating client from dictionary"""
        data = {
            'Type': 'client',
            'ID': 1,
            'Name': 'John Doe',
            'PhoneNumber': '555-1234'
        }

        record = create_record_from_dict(data)
        assert isinstance(record, Client)
        assert record.Name == 'John Doe'

    def test_create_record_from_dict_airline(self):
        """Test creating airline from dictionary"""
        data = {
            'Type': 'airline',
            'ID': 1,
            'CompanyName': 'Delta Airlines'
        }

        record = create_record_from_dict(data)
        assert isinstance(record, Airline)
        assert record.CompanyName == 'Delta Airlines'

    def test_create_record_from_dict_flight(self):
        """Test creating flight from dictionary"""
        data = {
            'Type': 'flight',
            'ID': 1,
            'Client_ID': 101,
            'Airline_ID': 201,
            'Date': '2024-12-15',
            'StartCity': 'New York',
            'EndCity': 'London'
        }

        record = create_record_from_dict(data)
        assert isinstance(record, Flight)
        assert record.StartCity == 'New York'

    def test_create_record_from_dict_unknown_type(self):
        """Test creating record with unknown type"""
        data = {
            'Type': 'unknown',
            'ID': 1
        }

        with pytest.raises(ValueError, match="Unknown record type"):
            create_record_from_dict(data)

    def test_create_record_from_dict_missing_type(self):
        """Test creating record without type"""
        data = {'ID': 1, 'Name': 'John Doe'}

        # Should raise ValueError when type is missing
        with pytest.raises(ValueError):
            create_record_from_dict(data)

    def test_validate_record_success(self):
        """Test successful record validation"""
        data = {
            'Type': 'client',
            'ID': 1,
            'Name': 'John Doe',
            'PhoneNumber': '555-1234',
            'City': 'New York',
            'Country': 'USA'
        }

        # Should not raise
        validate_record(data)

    def test_validate_record_failure(self):
        """Test record validation failure"""
        data = {
            'Type': 'client',
            'ID': 1,
            'Name': '',  # Missing name
            'PhoneNumber': '555-1234'
        }

        with pytest.raises(ValueError):
            validate_record(data)


class TestFieldNameConversion:
    """Test field name conversion between frontend and backend"""

    def test_client_field_conversion(self):
        """Test client field name conversion"""
        # Backend to frontend
        client = Client(ID=1, PhoneNumber="555-1234", ZipCode="10001")
        frontend_dict = client.to_dict()

        assert 'Phone Number' in frontend_dict
        assert frontend_dict['Phone Number'] == "555-1234"
        assert 'Zip Code' in frontend_dict
        assert frontend_dict['Zip Code'] == "10001"

        # Frontend to backend
        frontend_data = {
            'Phone Number': '555-9999',
            'Zip Code': '20002'
        }
        client2 = Client.from_frontend_dict(frontend_data)

        assert client2.PhoneNumber == "555-9999"
        assert client2.ZipCode == "20002"

    def test_airline_field_conversion(self):
        """Test airline field name conversion"""
        # Backend to frontend
        airline = Airline(ID=1, CompanyName="Test Airlines")
        frontend_dict = airline.to_dict()

        assert 'Company Name' in frontend_dict
        assert frontend_dict['Company Name'] == "Test Airlines"

        # Frontend to backend
        frontend_data = {'Company Name': 'Another Airline'}
        airline2 = Airline.from_frontend_dict(frontend_data)

        assert airline2.CompanyName == "Another Airline"

    def test_flight_field_conversion(self):
        """Test flight field name conversion"""
        # Backend to frontend
        flight = Flight(
            ID=1,
            Client_ID=101,
            Airline_ID=201,
            Date="2024-12-15",
            StartCity="Paris",
            EndCity="Rome"
        )
        frontend_dict = flight.to_dict()

        assert 'Start City' in frontend_dict
        assert frontend_dict['Start City'] == "Paris"
        assert 'End City' in frontend_dict
        assert frontend_dict['End City'] == "Rome"

        # Frontend to backend
        frontend_data = {
            'Start City': 'Berlin',
            'End City': 'Madrid'
        }
        flight2 = Flight.from_frontend_dict(frontend_data)

        assert flight2.StartCity == "Berlin"
        assert flight2.EndCity == "Madrid"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_client_with_minimal_data(self):
        """Test client creation with minimal required data"""
        client = Client(
            ID=1,
            Name="Minimal Client",
            PhoneNumber="123",
            City="Test",
            Country="Test"
        )

        client.validate()  # Should pass with only required fields

    def test_flight_with_simple_date(self):
        """Test flight with simple date format"""
        flight = Flight(
            ID=1,
            Client_ID=101,
            Airline_ID=201,
            Date="2024-12-15",  # Simple date
            StartCity="A",
            EndCity="B"
        )

        flight.validate()  # Should accept simple date

    def test_flight_with_datetime_local(self):
        """Test flight with datetime-local format"""
        flight = Flight(
            ID=1,
            Client_ID=101,
            Airline_ID=201,
            Date="2024-12-15T14:30",  # datetime-local format
            StartCity="A",
            EndCity="B"
        )

        flight.validate()  # Should accept datetime-local

    def test_negative_id(self):
        """Test with negative ID (should fail validation)"""
        client = Client(ID=-1, Name="Test", PhoneNumber="123", City="Test", Country="Test")

        with pytest.raises(ValueError, match="ID must be positive integer"):
            client.validate()

    def test_whitespace_validation(self):
        """Test that whitespace-only fields fail validation"""
        client = Client(
            ID=1,
            Name="   ",  # Only whitespace
            PhoneNumber="555-1234",
            City="New York",
            Country="USA"
        )

        with pytest.raises(ValueError, match="Client name is required"):
            client.validate()

    def test_none_values(self):
        """Test handling of None values"""
        client = Client(
            ID=1,
            Name=None,  # None value
            PhoneNumber="555-1234",
            City="New York",
            Country="USA"
        )

        # Name should be converted to empty string
        assert client.Name == ""

        with pytest.raises(ValueError, match="Client name is required"):
            client.validate()