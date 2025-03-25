class LocationService {
    constructor(map) {
        this.map = map;
        this.userMarker = null;
        this.accuracyCircle = null;
        this.watchId = null;
    }

    // Start tracking user location
    startTracking() {
        if ("geolocation" in navigator) {
            // Get initial position with longer timeout
            navigator.geolocation.getCurrentPosition(
                position => this.updatePosition(position),
                error => this.handleError(error),
                {
                    enableHighAccuracy: true,
                    timeout: 15000,  // Increased timeout to 15 seconds
                    maximumAge: 0
                }
            );

            // Watch for position changes
            this.watchId = navigator.geolocation.watchPosition(
                position => this.updatePosition(position),
                error => this.handleError(error),
                {
                    enableHighAccuracy: true,
                    timeout: 15000,  // Increased timeout to 15 seconds
                    maximumAge: 0
                }
            );
        } else {
            this.showError("Geolocation is not supported by your browser");
        }
    }

    // Stop tracking user location
    stopTracking() {
        if (this.watchId !== null) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }
    }

    // Get current position once
    getCurrentPosition() {
        navigator.geolocation.getCurrentPosition(
            position => this.updatePosition(position),
            error => this.handleError(error),
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );
    }

    // Update user's position on the map
    updatePosition(position) {
        const { latitude, longitude, accuracy } = position.coords;
        const latlng = L.latLng(latitude, longitude);

        // Create or update user marker
        if (!this.userMarker) {
            // Create user location marker
            this.userMarker = L.marker(latlng, {
                icon: L.divIcon({
                    className: 'user-location-marker',
                    html: '<div class="user-location-dot"></div>',
                    iconSize: [20, 20],
                    iconAnchor: [10, 10]
                })
            }).addTo(this.map);

            // Create accuracy circle
            this.accuracyCircle = L.circle(latlng, {
                radius: accuracy,
                fillColor: '#4A90E2',
                fillOpacity: 0.15,
                color: '#4A90E2',
                opacity: 0.3,
                weight: 2
            }).addTo(this.map);

            // Center map on user's location initially
            this.map.setView(latlng, 15);
        } else {
            // Update existing marker and circle
            this.userMarker.setLatLng(latlng);
            this.accuracyCircle.setLatLng(latlng);
            this.accuracyCircle.setRadius(accuracy);
        }

        // Trigger custom event with location data
        const event = new CustomEvent('userLocationUpdated', {
            detail: { latitude, longitude, accuracy }
        });
        document.dispatchEvent(event);
    }

    // Handle location errors
    handleError(error) {
        let message;
        switch(error.code) {
            case error.PERMISSION_DENIED:
                message = "Please enable location services to use this feature.";
                break;
            case error.POSITION_UNAVAILABLE:
                message = "Location information is unavailable. Please try again.";
                break;
            case error.TIMEOUT:
                message = "Location request timed out. Please check your connection and try again.";
                break;
            default:
                message = "An unknown error occurred while getting your location.";
        }
        this.showError(message);
        
        // Trigger error event
        const event = new CustomEvent('locationError', {
            detail: { error: message }
        });
        document.dispatchEvent(event);
    }

    // Show error message to user
    showError(message) {
        const errorDiv = document.getElementById('locationError') || document.createElement('div');
        errorDiv.id = 'locationError';
        errorDiv.className = 'alert alert-warning alert-dismissible fade show';
        errorDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add to page if not already present
        if (!document.getElementById('locationError')) {
            const mapContainer = document.getElementById('map').parentElement;
            mapContainer.insertBefore(errorDiv, document.getElementById('map'));
        }
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorDiv.classList.remove('show');
            setTimeout(() => errorDiv.remove(), 150);
        }, 5000);
    }

    // Calculate distance between two points
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth's radius in km
        const dLat = this.toRad(lat2 - lat1);
        const dLon = this.toRad(lon2 - lon1);
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                 Math.cos(this.toRad(lat1)) * Math.cos(this.toRad(lat2)) *
                 Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    // Convert degrees to radians
    toRad(degrees) {
        return degrees * (Math.PI/180);
    }
}
