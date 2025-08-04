(async () => {
    /* load data about the alumni */
    let vrs_alumni = await getCSVData();

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
    var vrsIcon = L.icon({
        iconUrl: base_url+'/++theme++isaw.theme/images/person-sharp.svg',
        iconSize:     [26, 26], // size of the icon
        iconAnchor:   [13, 13], // point of the icon which will correspond to marker's location
    });
    var vrs_alumni_markers = L.markerClusterGroup({
        spiderfyOnMaxZoom: true,
    });
    for(let i=0;i<vrs_alumni.length;i++) {
        console.log(i)
        let vrs_alumn = vrs_alumni[i]
	if (vrs_alumn["name"]===''){continue;}
        if (vrs_alumn["latitude"]==="") { continue; }
        if (vrs_alumn["longitude"]==="") { continue; }
        let lat_lon=[parseFloat(vrs_alumn["latitude"],10), parseFloat(vrs_alumn["longitude"],10)]
        vrs_alumni_markers.addLayer(
            L.marker(lat_lon, {icon:vrsIcon, alt:"Icon evoking the outline of a human head and shoulders."}).bindPopup(`
<h2><a href="${vrs_alumn.url}">${vrs_alumn.name}</a></h2>
<div class="map_html_blub">${vrs_alumn.html_blurb}<br/></div>
        `));
        isaw_bounds.extend(lat_lon);
    }
    map.addLayer(vrs_alumni_markers)

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
		Papa.parse('./@@people-listing-csv', {
			download:true,
			header:true,
			complete:(results) => {
				resolve(results.data);
			}
		});
	});
}


jQuery(function($) {
    function mapToggle(){
    event.preventDefault();
	$('div#map').slideToggle(
	    function(){
	    $('span#map_view').toggle();
	    $('span#map_hide').toggle();
	    window._leaflet_events.resize5_2();
	    }
	);
	}
    $('a#map-hide-show-link').on('click', mapToggle)
}
);
