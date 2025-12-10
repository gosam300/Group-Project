from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional


@dataclass
class Record:
    """Base record class"""
    ID: int
    Type: str

    def to_dict(self) -> dict:
        """Convert record to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Record":
        """Create record from dictionary"""
        return cls(**data)

    def validate(self) -> None:
        """Validate record data"""
        if not isinstance(self.ID, int):
            raise ValueError("ID must be int")
        if self.ID <= 0:
            raise ValueError("ID must be positive integer")


@dataclass
class Client(Record):
    """Client record with address information"""
    Name: str = ""
    PhoneNumber: str = ""
    Address1: str = ""
    Address2: str = ""
    Address3: str = ""
    City: str = ""
    State: str = ""
    ZipCode: str = ""
    Country: str = ""
    Type: str = field(default="client", init=False)  # Fixed value

    def __post_init__(self):
        """Initialize after dataclass creation"""
        # Set Type to 'client' regardless of input
        object.__setattr__(self, 'Type', 'client')
        # Ensure ID is integer
        if not isinstance(self.ID, int):
            object.__setattr__(self, 'ID', int(self.ID))

    def to_dict(self) -> dict:
        """Convert to dictionary with frontend-compatible field names"""
        data = super().to_dict()
        # Map to frontend field names
        return {
            'ID': data['ID'],
            'Type': data['Type'],
            'Name': data['Name'],
            'Phone Number': data['PhoneNumber'],
            'Address Line 1': data['Address1'],
            'Address Line 2': data['Address2'],
            'Address Line 3': data['Address3'],
            'City': data['City'],
            'State': data['State'],
            'Zip Code': data['ZipCode'],
            'Country': data['Country']
        }

    @classmethod
    def from_frontend_dict(cls, data: dict) -> "Client":
        """Create client from frontend dictionary format"""
        # Convert frontend field names to model field names
        return cls(
            ID=data.get('ID', 0),
            Name=data.get('Name', ''),
            PhoneNumber=data.get('Phone Number', ''),
            Address1=data.get('Address Line 1', ''),
            Address2=data.get('Address Line 2', ''),
            Address3=data.get('Address Line 3', ''),
            City=data.get('City', ''),
            State=data.get('State', ''),
            ZipCode=data.get('Zip Code', ''),
            Country=data.get('Country', '')
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Client":
        """Create from both frontend and backend dictionary formats"""
        # Check if using frontend field names
        if 'Phone Number' in data:
            return cls.from_frontend_dict(data)
        # Otherwise use direct mapping
        return cls(
            ID=data.get('ID', 0),
            Name=data.get('Name', ''),
            PhoneNumber=data.get('PhoneNumber', ''),
            Address1=data.get('Address1', ''),
            Address2=data.get('Address2', ''),
            Address3=data.get('Address3', ''),
            City=data.get('City', ''),
            State=data.get('State', ''),
            ZipCode=data.get('ZipCode', ''),
            Country=data.get('Country', '')
        )

    def validate(self) -> None:
        """Validate client data"""
        super().validate()
        if not self.Name or not self.Name.strip():
            raise ValueError("Client name is required")
        if not self.PhoneNumber or not self.PhoneNumber.strip():
            raise ValueError("Phone number is required")
        if not self.City or not self.City.strip():
            raise ValueError("City is required")
        if not self.Country or not self.Country.strip():
            raise ValueError("Country is required")


@dataclass
class Airline(Record):
    """Airline company record"""
    CompanyName: str = ""
    Type: str = field(default="airline", init=False)  # Fixed value

    def __post_init__(self):
        """Initialize after dataclass creation"""
        object.__setattr__(self, 'Type', 'airline')
        if not isinstance(self.ID, int):
            object.__setattr__(self, 'ID', int(self.ID))

    def to_dict(self) -> dict:
        """Convert to dictionary with frontend-compatible field names"""
        data = super().to_dict()
        return {
            'ID': data['ID'],
            'Type': data['Type'],
            'Company Name': data['CompanyName']
        }

    @classmethod
    def from_frontend_dict(cls, data: dict) -> "Airline":
        """Create airline from frontend dictionary format"""
        return cls(
            ID=data.get('ID', 0),
            CompanyName=data.get('Company Name', '')
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Airline":
        """Create from both frontend and backend dictionary formats"""
        if 'Company Name' in data:
            return cls.from_frontend_dict(data)
        return cls(
            ID=data.get('ID', 0),
            CompanyName=data.get('CompanyName', '')
        )

    def validate(self) -> None:
        """Validate airline data"""
        super().validate()
        if not self.CompanyName or not self.CompanyName.strip():
            raise ValueError("Company name is required")


@dataclass
class Flight(Record):
    """Flight record linking client and airline"""
    Client_ID: int = 0
    Airline_ID: int = 0
    Date: str = ""
    StartCity: str = ""
    EndCity: str = ""
    Type: str = field(default="flight", init=False)  # Fixed value

    def __post_init__(self):
        """Initialize after dataclass creation"""
        object.__setattr__(self, 'Type', 'flight')
        if not isinstance(self.ID, int):
            object.__setattr__(self, 'ID', int(self.ID))
        if not isinstance(self.Client_ID, int):
            object.__setattr__(self, 'Client_ID', int(self.Client_ID))
        if not isinstance(self.Airline_ID, int):
            object.__setattr__(self, 'Airline_ID', int(self.Airline_ID))

    def to_dict(self) -> dict:
        """Convert to dictionary with frontend-compatible field names"""
        data = super().to_dict()
        return {
            'ID': data['ID'],
            'Type': data['Type'],
            'Client_ID': data['Client_ID'],
            'Airline_ID': data['Airline_ID'],
            'Date': data['Date'],
            'Start City': data['StartCity'],
            'End City': data['EndCity']
        }

    @classmethod
    def from_frontend_dict(cls, data: dict) -> "Flight":
        """Create flight from frontend dictionary format"""
        return cls(
            ID=data.get('ID', 0),
            Client_ID=data.get('Client_ID', 0),
            Airline_ID=data.get('Airline_ID', 0),
            Date=data.get('Date', ''),
            StartCity=data.get('Start City', ''),
            EndCity=data.get('End City', '')
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Flight":
        """Create from both frontend and backend dictionary formats"""
        if 'Start City' in data:
            return cls.from_frontend_dict(data)
        return cls(
            ID=data.get('ID', 0),
            Client_ID=data.get('Client_ID', 0),
            Airline_ID=data.get('Airline_ID', 0),
            Date=data.get('Date', ''),
            StartCity=data.get('StartCity', ''),
            EndCity=data.get('EndCity', '')
        )

    def validate(self) -> None:
        """Validate flight data"""
        super().validate()

        if self.Client_ID <= 0:
            raise ValueError("Client ID must be positive integer")
        if self.Airline_ID <= 0:
            raise ValueError("Airline ID must be positive integer")

        # Validate date
        try:
            # Handle both ISO format and datetime-local input
            if 'T' in self.Date:
                datetime.fromisoformat(self.Date.replace('Z', '+00:00'))
            else:
                datetime.strptime(self.Date, '%Y-%m-%d')
        except (ValueError, TypeError):
            raise ValueError(f"Invalid date format: {self.Date}. Use YYYY-MM-DD or ISO format")

        if not self.StartCity or not self.StartCity.strip():
            raise ValueError("Start city is required")
        if not self.EndCity or not self.EndCity.strip():
            raise ValueError("End city is required")


# Type aliases for better type hints
RecordType = Client | Airline | Flight


def create_record_from_dict(data: dict) -> RecordType:
    """Factory function to create appropriate record from dictionary"""
    record_type = data.get('Type', '').lower()

    if record_type == 'client':
        return Client.from_dict(data)
    elif record_type == 'airline':
        return Airline.from_dict(data)
    elif record_type == 'flight':
        return Flight.from_dict(data)
    else:
        raise ValueError(f"Unknown record type: {record_type}")


def validate_record(data: dict) -> None:
    """Validate record data before saving"""
    record = create_record_from_dict(data)
    record.validate()


# Example usage
if __name__ == "__main__":
    # Test client creation
    client_data = {
        'ID': 1,
        'Name': 'John Doe',
        'Phone Number': '555-1234',
        'Address Line 1': '123 Main St',
        'City': 'New York',
        'State': 'NY',
        'Zip Code': '10001',
        'Country': 'USA'
    }

    client = Client.from_frontend_dict(client_data)
    print("Client dict:", client.to_dict())
    client.validate()
    print("Client validation passed!")

    # Test airline creation
    airline_data = {
        'ID': 1,
        'Company Name': 'Delta Airlines'
    }

    airline = Airline.from_frontend_dict(airline_data)
    print("\nAirline dict:", airline.to_dict())
    airline.validate()
    print("Airline validation passed!")

    # Test flight creation
    flight_data = {
        'ID': 1,
        'Client_ID': 1,
        'Airline_ID': 1,
        'Date': '2024-12-15T14:30:00',
        'Start City': 'New York',
        'End City': 'London'
    }

    flight = Flight.from_frontend_dict(flight_data)
    print("\nFlight dict:", flight.to_dict())
    flight.validate()
    print("Flight validation passed!")