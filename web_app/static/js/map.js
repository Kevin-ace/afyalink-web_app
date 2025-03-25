// Initialize map and location service
const map = L.map('map').setView([-1.2921, 36.8219], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: ' OpenStreetMap contributors'
}).addTo(map);

// Initialize marker cluster group
const markerCluster = L.markerClusterGroup();
map.addLayer(markerCluster);

const locationService = new LocationService(map);
let isTrackingLocation = false;

// Toggle location tracking
function toggleLocationTracking() {
    const button = document.querySelector('[title="Your Location"]');
    if (isTrackingLocation) {
        locationService.stopTracking();
        button.classList.remove('active');
    } else {
        locationService.startTracking();
        button.classList.add('active');
    }
    isTrackingLocation = !isTrackingLocation;
}

// Listen for location updates
document.addEventListener('userLocationUpdated', function(e) {
    const { latitude, longitude } = e.detail;
    updateDistances(latitude, longitude);
});

// Update distances when user location changes
function updateDistances(userLat, userLon) {
    const items = document.querySelectorAll('#facilityList .facility-card');
    items.forEach(item => {
        const lat = parseFloat(item.dataset.latitude);
        const lon = parseFloat(item.dataset.longitude);
        const distance = locationService.calculateDistance(userLat, userLon, lat, lon);
        const distanceEl = item.querySelector('.distance');
        if (distanceEl) {
            distanceEl.textContent = `${distance.toFixed(1)} km away`;
        }
    });

    // Update sort if sorting by distance
    if (document.getElementById('sortBy').value === 'distance') {
        filterFacilities();
    }
}

// Sort facilities
function sortFacilities(by) {
    const facilityList = document.getElementById('facilityList');
    const items = Array.from(facilityList.children);

    items.sort((a, b) => {
        switch(by) {
            case 'name':
                return a.querySelector('h6').textContent.localeCompare(b.querySelector('h6').textContent);
            case 'type':
                return a.querySelector('.facility-type').textContent.localeCompare(b.querySelector('.facility-type').textContent);
            case 'distance':
                const distA = parseFloat(a.querySelector('.distance').textContent) || Infinity;
                const distB = parseFloat(b.querySelector('.distance').textContent) || Infinity;
                return distA - distB;
            default:
                return 0;
        }
    });

    items.forEach(item => facilityList.appendChild(item));
}

// Custom icons for different facility types
const facilityIcons = {
    '1': L.divIcon({
        className: 'facility-marker hospital',
        html: '<i class="fas fa-hospital"></i>',
        iconSize: [40, 40],
        iconAnchor: [20, 40],
        popupAnchor: [0, -40]
    }),
    '3': L.divIcon({
        className: 'facility-marker health-center',
        html: '<i class="fas fa-clinic-medical"></i>',
        iconSize: [35, 35],
        iconAnchor: [17.5, 35],
        popupAnchor: [0, -35]
    }),
    '4': L.divIcon({
        className: 'facility-marker dispensary',
        html: '<i class="fas fa-first-aid"></i>',
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30]
    })
};

let markers = [];
let facilities = [];
let currentLocation = null;

// Fetch facilities from API
async function fetchFacilities() {
    try {
        const response = await fetch('/api/facilities');
        facilities = await response.json();
        displayFacilities(facilities);
    } catch (error) {
        console.error('Error fetching facilities:', error);
    }
}

// Display facilities on map and in list
function displayFacilities(facilities) {
    // Clear existing markers and list
    markerCluster.clearLayers();
    markers = [];
    document.getElementById('facilityList').innerHTML = '';

    facilities.forEach(facility => {
        // Get appropriate icon based on facility type
        const icon = facilityIcons[facility.facility_type] || facilityIcons['4'];
        
        // Add marker to map
        const marker = L.marker([facility.latitude, facility.longitude], { icon: icon })
            .bindPopup(createPopupContent(facility));
        
        marker.on('mouseover', function() {
            this.openPopup();
        });
        
        markers.push(marker);
        markerCluster.addLayer(marker);

        // Add to sidebar list
        const facilityElement = document.createElement('div');
        facilityElement.innerHTML = createFacilityCard(facility);
        facilityElement.querySelector('.facility-card').addEventListener('click', () => {
            map.setView([facility.latitude, facility.longitude], 16);
            marker.openPopup();
        });
        facilityElement.querySelector('.facility-card').dataset.latitude = facility.latitude;
        facilityElement.querySelector('.facility-card').dataset.longitude = facility.longitude;
        document.getElementById('facilityList').appendChild(facilityElement);
    });
}

// Create popup content
function createPopupContent(facility) {
    return `
        <div class="facility-info">
            <h5>${facility.name}</h5>
            <p><strong>Type:</strong> ${getFacilityTypeName(facility.facility_type)}</p>
            <p><strong>Address:</strong> ${facility.address}</p>
            <p><strong>Services:</strong> ${facility.services}</p>
            <p><strong>Insurance:</strong> ${facility.insurance}</p>
        </div>
    `;
}

// Create facility card for sidebar
function createFacilityCard(facility) {
    const typeClass = `facility-type-${facility.facility_type.toLowerCase()}`;
    return `
        <div class="card facility-card ${typeClass} mb-3">
            <div class="card-body">
                <h6 class="card-title">${facility.name}</h6>
                <span class="badge bg-primary">${getFacilityTypeName(facility.facility_type)}</span>
                <p class="card-text small mt-2 mb-1">${facility.address}</p>
                <p class="card-text small text-muted">${facility.services}</p>
                <p class="distance"></p>
            </div>
        </div>
    `;
}

// Get facility type name
function getFacilityTypeName(type) {
    const types = {
        '1': 'Hospital',
        '3': 'Health Center',
        '4': 'Dispensary'
    };
    return types[type] || 'Other';
}

// Filter facilities
function filterFacilities() {
    const typeFilter = document.getElementById('facilityTypeFilter').value;
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const sortBy = document.getElementById('sortBy').value;

    let filtered = facilities.filter(facility => {
        const matchesType = !typeFilter || facility.facility_type === typeFilter;
        const matchesSearch = !searchInput || 
            facility.name.toLowerCase().includes(searchInput) ||
            facility.address.toLowerCase().includes(searchInput) ||
            facility.services.toLowerCase().includes(searchInput);
        return matchesType && matchesSearch;
    });

    // Sort facilities
    filtered.sort((a, b) => {
        if (sortBy === 'name') {
            return a.name.localeCompare(b.name);
        } else if (sortBy === 'type') {
            return a.facility_type.localeCompare(b.facility_type);
        } else if (sortBy === 'distance' && currentLocation) {
            const distA = locationService.calculateDistance(currentLocation[0], currentLocation[1], a.latitude, a.longitude);
            const distB = locationService.calculateDistance(currentLocation[0], currentLocation[1], b.latitude, b.longitude);
            return distA - distB;
        }
        return 0;
    });

    displayFacilities(filtered);
}

// Get user's location
function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            currentLocation = [position.coords.latitude, position.coords.longitude];
            
            // Add user marker
            L.marker(currentLocation, {
                icon: L.divIcon({
                    className: 'user-location',
                    html: '<div class="user-location-dot"></div>',
                    iconSize: [20, 20]
                })
            }).addTo(map);

            map.setView(currentLocation, 14);
        });
    }
}

// Event listeners
document.getElementById('facilityTypeFilter').addEventListener('change', filterFacilities);
document.getElementById('searchInput').addEventListener('input', filterFacilities);
document.getElementById('sortBy').addEventListener('change', filterFacilities);

// Initialize
fetchFacilities();
