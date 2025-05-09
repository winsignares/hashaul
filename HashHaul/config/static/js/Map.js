
function initMap() {
   
    const barranquilla = { lat: 10.9685, lng: -74.7813 };
    

    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 14,
        center: barranquilla,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        styles: [
            {
                "featureType": "all",
                "elementType": "labels.text.fill",
                "stylers": [{"color": "#ffffff"}]
            },
            {
                "featureType": "all",
                "elementType": "labels.text.stroke",
                "stylers": [{"visibility": "on"}, {"color": "#3e606f"}, {"weight": 2}, {"gamma": 0.84}]
            },
            {
                "featureType": "administrative",
                "elementType": "geometry",
                "stylers": [{"weight": 0.6}, {"color": "#1a3541"}]
            },
            {
                "featureType": "landscape",
                "elementType": "geometry",
                "stylers": [{"color": "#2c5a71"}]
            },
            {
                "featureType": "poi",
                "elementType": "geometry",
                "stylers": [{"color": "#406d80"}]
            },
            {
                "featureType": "road",
                "elementType": "geometry",
                "stylers": [{"color": "#29768a"}, {"lightness": -37}]
            },
            {
                "featureType": "transit",
                "elementType": "geometry",
                "stylers": [{"color": "#406d80"}]
            },
            {
                "featureType": "water",
                "elementType": "geometry",
                "stylers": [{"color": "#193341"}]
            }
        ]
    });
    
    
    const routeCoordinates = [
        { lat: 10.9885, lng: -74.7913 }, 
        { lat: 10.9835, lng: -74.7863 }, 
        { lat: 10.9785, lng: -74.7813 }, 
        { lat: 10.9735, lng: -74.7763 }, 
        { lat: 10.9685, lng: -74.7713 }, 
        { lat: 10.9635, lng: -74.7663 }, 
    ];
    
    
    const routePath = new google.maps.Polyline({
        path: routeCoordinates,
        geodesic: true,
        strokeColor: "#6200EA", 
        strokeOpacity: 1.0,
        strokeWeight: 5,
    });
    
   
    routePath.setMap(map);
    
    
    const startMarker = new google.maps.Marker({
        position: routeCoordinates[0],
        map: map,
        title: "Inicio: Parque Venezuela",
        icon: {
            url: "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
        }
    });
    
    const midMarker = new google.maps.Marker({
        position: routeCoordinates[2],
        map: map,
        title: "Checkpoint: Bancolombia Cajero",
        icon: {
            url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png"
        }
    });
    
    const endMarker = new google.maps.Marker({
        position: routeCoordinates[5],
        map: map,
        title: "Destino: Portal del Prado",
        icon: {
            url: "http://maps.google.com/mapfiles/ms/icons/green-dot.png"
        }
    });
    
    
    const infoWindow = new google.maps.InfoWindow({
        content: '<div style="color: black; font-weight: bold;">32 min<br>3.2 km</div>',
        position: { lat: 10.9785, lng: -74.7813 }
    });
    
    infoWindow.open(map);
}


window.onload = function() {
   
    if (typeof google === 'object' && typeof google.maps === 'object') {
        initMap();
    } else {
        console.error('Google Maps API no está cargada correctamente');
        document.getElementById('map').innerHTML = '<div style="text-align: center; padding: 20px;">Error al cargar el mapa. Por favor, verifica tu API key.</div>';
    }
};