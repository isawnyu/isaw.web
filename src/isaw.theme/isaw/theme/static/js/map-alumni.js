(async () => {
    /* load data about the alumni */
    let alumni = await getCSVData();

    /* set up the map, base tiles, controls, etc. */
    let map = L.map('map', {
        attributionControl:false,
        zoomSnap: 0.5,
        maxBounds: ([
            [-89.9, -179.9],
            [89.9, 179.9]
        ]),
        maxBoundsViscosity: 1.0,
        minZoom: 2,
    }).setView([0.0, 0.0], 1);
    L.tileLayer('https://api.maptiler.com/maps/topo-v2/{z}/{x}/{y}.png?key=Kv1hV81exhuxIocoEOos', {
        tileSize: 512,
        zoomOffset: -1,
        minZoom: 1,
        crossOrigin: true
    }).addTo(map);
    L.control.attribution({prefix:false}).addAttribution('<a href="https://leafletjs.com/">Leaflet</a> map by <a href="https://isaw.nyu.edu">ISAW NYU</a>. Base map "Topo" by <a href="https://cloud.maptiler.com">MapTiler</a>. Markers from <a href="https://ionic.io/ionicons">IonIcons</a>.').addTo(map)

    var isaw_bounds = L.latLngBounds()

    /* plot alumni locations */
    var alumIcon = L.icon({
        iconUrl: '../images/school-sharp.svg',
        iconSize:     [26, 26], // size of the icon
        iconAnchor:   [13, 13], // point of the icon which will correspond to marker's location
    });
    var alumni_markers = L.markerClusterGroup({
        spiderfyOnMaxZoom: true,
    });
    for(let i=0;i<alumni.length;i++) {
        console.log(i)
        let alumn = alumni[i]
        let lat_lon=[parseFloat(alumn["latitude"],10), parseFloat(alumn["longitude"],10)]
        alumni_markers.addLayer(
            L.marker(lat_lon, {icon:alumIcon, alt:"Icon of a mortar board hat worn by college graduates."}).bindPopup(`
<h2><a href="${alumn.profileuri}">${alumn.displayname}</a></h2>
<p>Class of ${alumn.year}<br>${alumn.title}</p>
        `));
        isaw_bounds.extend(lat_lon);
    }
    map.addLayer(alumni_markers)

    /* pan and zoom the map to fit all the content */
    map.fitBounds(isaw_bounds);

    L.control.ResetBounds({
        position: "topleft",
        title: "Reset view",
        bounds: isaw_bounds,
    }).addTo(map);

})();

async function getCSVData() {
	return new Promise((resolve, reject) => {
		Papa.parse('/isaw/people/students/alumni.csv', {
			download:true,
			header:true,
			complete:(results) => {
				resolve(results.data);
			}
		});
	});
}
