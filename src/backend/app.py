from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import sys
import os

# ============ SETUP PATHS ============
# Get the absolute paths
BACKEND_DIR = Path(__file__).parent  # Current directory (backend)
SRC_DIR = BACKEND_DIR.parent  # src directory
GUI_DIR = SRC_DIR / "gui"
DATA_DIR = SRC_DIR / "data"
RECORD_DIR = SRC_DIR / "record"

print("=" * 60)
print("SYSTEM PATHS CONFIGURATION")
print("=" * 60)
print(f"Backend directory: {BACKEND_DIR}")
print(f"Source directory: {SRC_DIR}")
print(f"GUI directory: {GUI_DIR} (exists: {GUI_DIR.exists()})")
print(f"Data directory: {DATA_DIR} (exists: {DATA_DIR.exists()})")
print(f"Record directory: {RECORD_DIR} (exists: {RECORD_DIR.exists()})")
print("=" * 60)

# Add all necessary directories to Python path
sys.path.insert(0, str(SRC_DIR))  # src directory first
sys.path.insert(0, str(DATA_DIR))  # data directory
sys.path.insert(0, str(BACKEND_DIR))  # backend directory

# Debug: Show Python path
print("Python search path:")
for i, path in enumerate(sys.path[:5]):  # Show first 5 paths
    print(f"  {i}. {path}")
print("  ...")
print("=" * 60)

# ============ INITIALIZE FLASK APP ============
app = Flask(__name__, static_folder=str(GUI_DIR))
CORS(app)  # Enable CORS for all routes

# ============ DATA FILE PATH ============
# Use JSON format instead of JSONL for simplicity
DATA_FILE = RECORD_DIR / "records.json"
print(f"Data file: {DATA_FILE.absolute()}")
print(f"Data file exists: {DATA_FILE.exists()}")

# Create directories if they don't exist
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

# ============ IMPORT AND INITIALIZE STORAGE ============
print("\nAttempting to import RecordStorage...")

try:
    # Try importing from data directory
    from record_storage import RecordStorage

    print("✓ Successfully imported RecordStorage from data directory")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Checking data directory contents:")
    if DATA_DIR.exists():
        for file in DATA_DIR.glob("*.py"):
            print(f"  - {file.name}")

    # Try absolute import as fallback
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "record_storage",
            DATA_DIR / "record_storage.py"
        )
        if spec is None:
            print(f"✗ Could not find record_storage.py in {DATA_DIR}")
            sys.exit(1)
        record_storage_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(record_storage_module)
        RecordStorage = record_storage_module.RecordStorage
        print("✓ Successfully imported RecordStorage via absolute path")
    except Exception as import_error:
        print(f"✗ Failed to import RecordStorage: {import_error}")
        sys.exit(1)

# Initialize storage
try:
    storage = RecordStorage(str(DATA_FILE))
    print(f"✓ Storage initialized with {len(storage.records)} records")
except Exception as e:
    print(f"✗ Error initializing storage: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("=" * 60)


# ============ ROUTES ============

# Route 1: Serve the main GUI application
@app.route('/')
def serve_gui():
    """Serve the main Vue.js application"""
    if not GUI_DIR.exists():
        return jsonify({"error": "GUI directory not found"}), 404

    index_path = GUI_DIR / "index.html"
    if not index_path.exists():
        return jsonify({
            "error": "index.html not found",
            "gui_directory": str(GUI_DIR),
            "files_in_gui": [f.name for f in GUI_DIR.glob("*")]
        }), 404

    return send_from_directory(str(GUI_DIR), 'index.html')


# Route 2: Serve static files from GUI directory
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, etc.)"""
    if not GUI_DIR.exists():
        return jsonify({"error": "GUI directory not found"}), 404

    file_path = GUI_DIR / filename
    if file_path.exists() and file_path.is_file():
        return send_from_directory(str(GUI_DIR), filename)
    else:
        # If file doesn't exist, try to serve index.html for Vue router
        if filename.startswith('api/'):
            # API calls should go to API routes
            pass
        else:
            # For any other path, serve index.html (for Vue Router)
            return send_from_directory(str(GUI_DIR), 'index.html')


# Route 3: API documentation
@app.route('/api/')
def api_root():
    """API documentation and endpoints list"""
    return jsonify({
        "message": "Record Management System API",
        "version": "1.0.0",
        "endpoints": {
            "clients": {
                "GET /api/clients": "Get all clients",
                "POST /api/clients": "Create new client",
                "GET /api/clients/<id>": "Get specific client",
                "PUT /api/clients/<id>": "Update client",
                "DELETE /api/clients/<id>": "Delete client"
            },
            "airlines": {
                "GET /api/airlines": "Get all airlines",
                "POST /api/airlines": "Create new airline",
                "GET /api/airlines/<id>": "Get specific airline",
                "PUT /api/airlines/<id>": "Update airline",
                "DELETE /api/airlines/<id>": "Delete airline"
            },
            "flights": {
                "GET /api/flights": "Get all flights",
                "POST /api/flights": "Create new flight",
                "GET /api/flights/<id>": "Get specific flight",
                "PUT /api/flights/<id>": "Update flight",
                "DELETE /api/flights/<id>": "Delete flight"
            },
            "utilities": {
                "GET /api/search": "Search records (params: type, field, value)",
                "GET /api/stats": "Get system statistics",
                "GET /api/health": "Health check"
            }
        }
    })


# ================== CLIENT ENDPOINTS ==================
@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Get all client records"""
    try:
        clients = storage.get_all_records('client')
        return jsonify(clients)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch clients: {str(e)}"}), 500


@app.route('/api/clients', methods=['POST'])
def create_client():
    """Create a new client record"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        data['Type'] = 'client'
        client = storage.add_record(data)
        return jsonify(client), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create client: {str(e)}"}), 500


@app.route('/api/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """Get a specific client by ID"""
    client = storage.get_record(client_id, 'client')
    if client:
        return jsonify(client)
    return jsonify({"error": f"Client with ID {client_id} not found"}), 404


@app.route('/api/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    """Update an existing client"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No update data provided"}), 400

        if storage.update_record(client_id, 'client', data):
            return jsonify({
                "message": f"Client {client_id} updated successfully",
                "client_id": client_id
            })
        return jsonify({"error": f"Client with ID {client_id} not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update client: {str(e)}"}), 500


@app.route('/api/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Delete a client record"""
    if storage.delete_record(client_id, 'client'):
        return jsonify({
            "message": f"Client {client_id} deleted successfully",
            "client_id": client_id
        })
    return jsonify({"error": f"Client with ID {client_id} not found"}), 404


# ================== AIRLINE ENDPOINTS ==================
@app.route('/api/airlines', methods=['GET'])
def get_airlines():
    """Get all airline records"""
    try:
        airlines = storage.get_all_records('airline')
        return jsonify(airlines)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch airlines: {str(e)}"}), 500


@app.route('/api/airlines', methods=['POST'])
def create_airline():
    """Create a new airline record"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        data['Type'] = 'airline'
        airline = storage.add_record(data)
        return jsonify(airline), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create airline: {str(e)}"}), 500


@app.route('/api/airlines/<int:airline_id>', methods=['GET'])
def get_airline(airline_id):
    """Get a specific airline by ID"""
    airline = storage.get_record(airline_id, 'airline')
    if airline:
        return jsonify(airline)
    return jsonify({"error": f"Airline with ID {airline_id} not found"}), 404


@app.route('/api/airlines/<int:airline_id>', methods=['PUT'])
def update_airline(airline_id):
    """Update an existing airline"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No update data provided"}), 400

        if storage.update_record(airline_id, 'airline', data):
            return jsonify({
                "message": f"Airline {airline_id} updated successfully",
                "airline_id": airline_id
            })
        return jsonify({"error": f"Airline with ID {airline_id} not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update airline: {str(e)}"}), 500


@app.route('/api/airlines/<int:airline_id>', methods=['DELETE'])
def delete_airline(airline_id):
    """Delete an airline record"""
    if storage.delete_record(airline_id, 'airline'):
        return jsonify({
            "message": f"Airline {airline_id} deleted successfully",
            "airline_id": airline_id
        })
    return jsonify({"error": f"Airline with ID {airline_id} not found"}), 404


# ================== FLIGHT ENDPOINTS ==================
@app.route('/api/flights', methods=['GET'])
def get_flights():
    """Get all flight records"""
    try:
        flights = storage.get_all_records('flight')
        return jsonify(flights)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch flights: {str(e)}"}), 500


@app.route('/api/flights', methods=['POST'])
def create_flight():
    """Create a new flight record"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        data['Type'] = 'flight'

        # Validate referenced client and airline
        client_id = data.get('Client_ID')
        airline_id = data.get('Airline_ID')

        if not client_id or not airline_id:
            return jsonify({"error": "Client_ID and Airline_ID are required"}), 400

        if not storage.get_record(client_id, 'client'):
            return jsonify({"error": f"Client with ID {client_id} not found"}), 400
        if not storage.get_record(airline_id, 'airline'):
            return jsonify({"error": f"Airline with ID {airline_id} not found"}), 400

        flight = storage.add_record(data)
        return jsonify(flight), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create flight: {str(e)}"}), 500


@app.route('/api/flights/<int:flight_id>', methods=['GET'])
def get_flight(flight_id):
    """Get a specific flight by ID"""
    flight = storage.get_record(flight_id, 'flight')
    if flight:
        return jsonify(flight)
    return jsonify({"error": f"Flight with ID {flight_id} not found"}), 404


@app.route('/api/flights/<int:flight_id>', methods=['PUT'])
def update_flight(flight_id):
    """Update an existing flight"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No update data provided"}), 400

        # Validate referenced client and airline if provided
        client_id = data.get('Client_ID')
        airline_id = data.get('Airline_ID')

        if client_id and not storage.get_record(client_id, 'client'):
            return jsonify({"error": f"Client with ID {client_id} not found"}), 400
        if airline_id and not storage.get_record(airline_id, 'airline'):
            return jsonify({"error": f"Airline with ID {airline_id} not found"}), 400

        if storage.update_record(flight_id, 'flight', data):
            return jsonify({
                "message": f"Flight {flight_id} updated successfully",
                "flight_id": flight_id
            })
        return jsonify({"error": f"Flight with ID {flight_id} not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update flight: {str(e)}"}), 500


@app.route('/api/flights/<int:flight_id>', methods=['DELETE'])
def delete_flight(flight_id):
    """Delete a flight record"""
    if storage.delete_record(flight_id, 'flight'):
        return jsonify({
            "message": f"Flight {flight_id} deleted successfully",
            "flight_id": flight_id
        })
    return jsonify({"error": f"Flight with ID {flight_id} not found"}), 404


# ================== SEARCH ENDPOINT ==================
@app.route('/api/search', methods=['GET'])
def search_records():
    """Search records by type, field, and value"""
    try:
        record_type = request.args.get('type', '')
        field = request.args.get('field', 'all')
        value = request.args.get('value', '')

        if not record_type:
            return jsonify({"error": "Record type is required (type=client|airline|flight)"}), 400
        if not value:
            return jsonify({"error": "Search value is required"}), 400

        results = storage.search_records(record_type, field, value)
        return jsonify({
            "results": results,
            "count": len(results),
            "parameters": {
                "type": record_type,
                "field": field,
                "value": value
            }
        })
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500


# ================== STATISTICS ENDPOINT ==================
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        clients = storage.get_all_records('client')
        airlines = storage.get_all_records('airline')
        flights = storage.get_all_records('flight')

        total_clients = len(clients)
        total_airlines = len(airlines)
        total_flights = len(flights)

        # Get unique cities from flights
        start_cities = set()
        end_cities = set()
        for flight in flights:
            if 'Start City' in flight:
                start_cities.add(flight['Start City'])
            if 'End City' in flight:
                end_cities.add(flight['End City'])

        return jsonify({
            "statistics": {
                "clients": total_clients,
                "airlines": total_airlines,
                "flights": total_flights,
                "total_records": total_clients + total_airlines + total_flights
            },
            "flight_analysis": {
                "unique_start_cities": len(start_cities),
                "unique_end_cities": len(end_cities),
                "start_cities": list(start_cities),
                "end_cities": list(end_cities)
            }
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get statistics: {str(e)}"}), 500


# ================== HEALTH CHECK ENDPOINT ==================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test storage connectivity
        record_count = len(storage.records)

        # Test file access
        file_exists = DATA_FILE.exists()
        file_size = DATA_FILE.stat().st_size if file_exists else 0

        return jsonify({
            "status": "healthy",
            "timestamp": os.path.getmtime(str(DATA_FILE)) if file_exists else None,
            "storage": {
                "connected": True,
                "record_count": record_count
            },
            "file_system": {
                "data_file": str(DATA_FILE),
                "exists": file_exists,
                "size_bytes": file_size
            },
            "system": {
                "python_version": sys.version,
                "platform": sys.platform
            }
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


# ================== ERROR HANDLERS ==================
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist.",
        "available_endpoints": ["/", "/api/", "/api/clients", "/api/airlines", "/api/flights", "/api/search",
                                "/api/stats", "/api/health"]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred on the server."
    }), 500


# ================== MAIN APPLICATION ==================
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("RECORD MANAGEMENT SYSTEM")
    print("=" * 60)
    print(f"🚀 Application is running!")
    print(f"🌐 Frontend GUI: http://localhost:5000")
    print(f"🔧 API Base URL: http://localhost:5000/api/")
    print(f"📊 API Documentation: http://localhost:5000/api/")
    print(f"❤️  Health Check: http://localhost:5000/api/health")
    print(f"💾 Data File: {DATA_FILE}")
    print(f"📈 Records Loaded: {len(storage.records)}")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")

    # Run the Flask application
    app.run(debug=True, port=5000, host='0.0.0.0')