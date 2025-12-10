const { createApp, ref, reactive, computed, onMounted } = Vue;

createApp({
    setup() {
        // State
        const activeTab = ref('clients');
        const clients = ref([]);
        const airlines = ref([]);
        const flights = ref([]);
        const searchResults = ref(null);
        const loading = reactive({
            clients: true,
            airlines: true,
            flights: true
        });
        const showDeleteModal = ref(false);
        const deleteRecordType = ref('');
        const deleteRecordId = ref(null);
        const statusMessage = ref('');
        const statusType = ref('');

        // Editing flags
        const editingClient = ref(false);
        const editingAirline = ref(false);
        const editingFlight = ref(false);

        // Form data
        const clientForm = reactive({
            Name: '',
            'Phone Number': '',
            'Address Line 1': '',
            'Address Line 2': '',
            'Address Line 3': '',
            City: '',
            State: '',
            'Zip Code': '',
            Country: ''
        });

        const airlineForm = reactive({
            'Company Name': ''
        });

        const flightForm = reactive({
            Client_ID: '',
            Airline_ID: '',
            Date: '',
            'Start City': '',
            'End City': ''
        });

        const searchForm = reactive({
            type: 'all',
            field: 'all',
            term: ''
        });

        // API Base URL
        const API_BASE = 'http://localhost:5000/api';

        // Helper Functions
        function formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleString();
        }

        function formatFieldName(field) {
            return field.replace(/([A-Z])/g, ' $1').replace(/_/g, ' ');
        }

        function formatType(type) {
            const types = {
                'client': 'Client',
                'airline': 'Airline',
                'flight': 'Flight'
            };
            return types[type] || type;
        }

        function getSearchFields() {
            const fields = {
                clients: ['Name', 'Phone Number', 'City', 'Country', 'State'],
                airlines: ['Company Name'],
                flights: ['Start City', 'End City']
            };
            return fields[searchForm.type] || [];
        }

        function getClientName(clientId) {
            const client = clients.value.find(c => c.ID === clientId);
            return client ? client.Name : `Client #${clientId}`;
        }

        function getAirlineName(airlineId) {
            const airline = airlines.value.find(a => a.ID === airlineId);
            return airline ? airline['Company Name'] : `Airline #${airlineId}`;
        }

        function showStatus(message, type = 'status-success') {
            statusMessage.value = message;
            statusType.value = type;
            setTimeout(() => {
                clearStatus();
            }, 5000);
        }

        function clearStatus() {
            statusMessage.value = '';
            statusType.value = '';
        }

        // API Functions
        async function fetchAll() {
            try {
                loading.clients = true;
                loading.airlines = true;
                loading.flights = true;

                const [clientsRes, airlinesRes, flightsRes] = await Promise.all([
                    fetch(`${API_BASE}/clients`).then(r => r.json()),
                    fetch(`${API_BASE}/airlines`).then(r => r.json()),
                    fetch(`${API_BASE}/flights`).then(r => r.json())
                ]);

                clients.value = clientsRes;
                airlines.value = airlinesRes;
                flights.value = flightsRes;

                showStatus('Data loaded successfully');
            } catch (error) {
                console.error('Error loading data:', error);
                showStatus('Failed to load data', 'status-error');
            } finally {
                loading.clients = false;
                loading.airlines = false;
                loading.flights = false;
            }
        }

        // Client CRUD
        async function createClient() {
            try {
                const response = await fetch(`${API_BASE}/clients`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(clientForm)
                });

                if (!response.ok) throw new Error('Failed to create client');

                resetForm('client');
                await fetchAll();
                showStatus('Client created successfully');
            } catch (error) {
                console.error('Error creating client:', error);
                showStatus('Failed to create client', 'status-error');
            }
        }

        function editClient(client) {
            editingClient.value = true;
            Object.assign(clientForm, client);
            // Scroll to top of form
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        async function updateClient() {
            try {
                const response = await fetch(`${API_BASE}/clients/${clientForm.ID}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(clientForm)
                });

                if (!response.ok) throw new Error('Failed to update client');

                resetForm('client');
                await fetchAll();
                showStatus('Client updated successfully');
            } catch (error) {
                console.error('Error updating client:', error);
                showStatus('Failed to update client', 'status-error');
            }
        }

        // Airline CRUD
        async function createAirline() {
            try {
                const response = await fetch(`${API_BASE}/airlines`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(airlineForm)
                });

                if (!response.ok) throw new Error('Failed to create airline');

                resetForm('airline');
                await fetchAll();
                showStatus('Airline created successfully');
            } catch (error) {
                console.error('Error creating airline:', error);
                showStatus('Failed to create airline', 'status-error');
            }
        }

        function editAirline(airline) {
            editingAirline.value = true;
            Object.assign(airlineForm, airline);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        async function updateAirline() {
            try {
                const response = await fetch(`${API_BASE}/airlines/${airlineForm.ID}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(airlineForm)
                });

                if (!response.ok) throw new Error('Failed to update airline');

                resetForm('airline');
                await fetchAll();
                showStatus('Airline updated successfully');
            } catch (error) {
                console.error('Error updating airline:', error);
                showStatus('Failed to update airline', 'status-error');
            }
        }

        // Flight CRUD
        async function createFlight() {
            try {
                const response = await fetch(`${API_BASE}/flights`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(flightForm)
                });

                if (!response.ok) throw new Error('Failed to create flight');

                resetForm('flight');
                await fetchAll();
                showStatus('Flight created successfully');
            } catch (error) {
                console.error('Error creating flight:', error);
                showStatus('Failed to create flight', 'status-error');
            }
        }

        function editFlight(flight) {
            editingFlight.value = true;
            // Convert date to local datetime format
            const flightDate = new Date(flight.Date);
            const localDate = flightDate.toISOString().slice(0, 16);

            Object.assign(flightForm, {
                ...flight,
                Date: localDate
            });
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        async function updateFlight() {
            try {
                const response = await fetch(`${API_BASE}/flights/${flightForm.ID}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(flightForm)
                });

                if (!response.ok) throw new Error('Failed to update flight');

                resetForm('flight');
                await fetchAll();
                showStatus('Flight updated successfully');
            } catch (error) {
                console.error('Error updating flight:', error);
                showStatus('Failed to update flight', 'status-error');
            }
        }

        // Delete Record
        function deleteRecord(type, id) {
            deleteRecordType.value = type;
            deleteRecordId.value = id;
            showDeleteModal.value = true;
        }

        async function confirmDelete() {
            try {
                const endpoint = deleteRecordType.value === 'clients' ? 'clients' :
                                deleteRecordType.value === 'airlines' ? 'airlines' : 'flights';

                const response = await fetch(`${API_BASE}/${endpoint}/${deleteRecordId.value}`, {
                    method: 'DELETE'
                });

                if (!response.ok) throw new Error('Failed to delete record');

                await fetchAll();
                showDeleteModal.value = false;
                showStatus(`${formatType(deleteRecordType.value)} deleted successfully`);
            } catch (error) {
                console.error('Error deleting record:', error);
                showStatus('Failed to delete record', 'status-error');
            }
        }

        // Search
        async function doSearch() {
            if (!searchForm.term.trim()) {
                searchResults.value = null;
                showStatus('Please enter a search term', 'status-warning');
                return;
            }

            try {
                let results = [];

                if (searchForm.type === 'all') {
                    // Search all record types
                    const [clientsRes, airlinesRes, flightsRes] = await Promise.all([
                        fetch(`${API_BASE}/search?type=client&field=${searchForm.field}&value=${searchForm.term}`).then(r => r.json()),
                        fetch(`${API_BASE}/search?type=airline&field=${searchForm.field}&value=${searchForm.term}`).then(r => r.json()),
                        fetch(`${API_BASE}/search?type=flight&field=${searchForm.field}&value=${searchForm.term}`).then(r => r.json())
                    ]);

                    results = [
                        ...clientsRes.map(r => ({ ...r, Type: 'client' })),
                        ...airlinesRes.map(r => ({ ...r, Type: 'airline' })),
                        ...flightsRes.map(r => ({ ...r, Type: 'flight' }))
                    ];
                } else {
                    // Search specific type
                    const response = await fetch(
                        `${API_BASE}/search?type=${searchForm.type}&field=${searchForm.field}&value=${searchForm.term}`
                    );
                    results = await response.json();
                }

                searchResults.value = results;
                showStatus(`Found ${results.length} records matching "${searchForm.term}"`);
            } catch (error) {
                console.error('Search error:', error);
                showStatus('Search failed', 'status-error');
            }
        }

        function clearSearch() {
            searchForm.type = 'all';
            searchForm.field = 'all';
            searchForm.term = '';
            searchResults.value = null;
        }

        // Form Helpers
        function resetForm(type) {
            switch(type) {
                case 'client':
                    Object.keys(clientForm).forEach(key => {
                        clientForm[key] = '';
                    });
                    editingClient.value = false;
                    break;
                case 'airline':
                    Object.keys(airlineForm).forEach(key => {
                        airlineForm[key] = '';
                    });
                    editingAirline.value = false;
                    break;
                case 'flight':
                    Object.keys(flightForm).forEach(key => {
                        flightForm[key] = '';
                    });
                    editingFlight.value = false;
                    break;
            }
        }

        function cancelEdit(type) {
            resetForm(type);
            showStatus('Edit cancelled');
        }

        // Lifecycle
        onMounted(() => {
            fetchAll();
        });

        return {
            // State
            activeTab,
            clients,
            airlines,
            flights,
            searchResults,
            loading,
            showDeleteModal,
            deleteRecordType,
            deleteRecordId,
            statusMessage,
            statusType,

            // Editing flags
            editingClient,
            editingAirline,
            editingFlight,

            // Form data
            clientForm,
            airlineForm,
            flightForm,
            searchForm,

            // Helper functions
            formatDate,
            formatFieldName,
            formatType,
            getSearchFields,
            getClientName,
            getAirlineName,
            showStatus,
            clearStatus,

            // CRUD operations
            createClient,
            editClient,
            updateClient,
            createAirline,
            editAirline,
            updateAirline,
            createFlight,
            editFlight,
            updateFlight,
            deleteRecord,
            confirmDelete,

            // Search
            doSearch,
            clearSearch,

            // Form helpers
            cancelEdit
        };
    }
}).mount('#app');