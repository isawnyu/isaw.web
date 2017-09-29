/*global google:true, jQuery:true, L:true*/
jQuery(function($) {
    var L = window.L || {Icon: {Default: {}}};
	$('h3.trigger').click(function(){
		$(this).toggleClass('open');
		$('#main-navigation').toggleClass('open');
	});
    var nav_folders = $('ul.navTree li.navTreeFolderish');
    nav_folders.each(function (i, e) {
        var folder = $(e);
        if (folder.children().length < 2) {
            folder.addClass('collapsed');
        }
    });
    var $slider_containers = $('#slider-container, #slider');
    var $slides = $('#slider .slide');
    var $images = $('#slider .slide img');
    function resize_slider() {
        var $slide_list = $('#slider .slider-list');
        var slide_count = $slides.length;

        $slides.css('width', $(window).width()).css('height', 'auto');
        $images.css('width', '100%').css('height', 'auto');

        $slide_list.width($slides.width()*slide_count);
        $slide_list.css('max-width', 100*slide_count + '%');
        $slides.css('max-width', 100/slide_count + '%');

        $slider_containers.css('width', $(window).width());
        $slider_containers.css('height', $slides.height());
    }
    // Ideally we would listen for window resizes, but EasySlider sets the
    // width for scrolling one time only.
    resize_slider();
    $(window).load(resize_slider);
    $images.load(resize_slider);
    /*capture the search link click and open the drawer*/
    $('#secondary #siteaction-search a').click(function(e){
	   e.preventDefault();
	   $('#portal-searchbox').slideToggle();
    });
    
    /* close aliens invaded message */
    $('#emergency-message .close').click(function() {
        var date = new Date();
        date.setTime(date.getTime()+(1*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
        document.cookie = "isaw-emergency-read=yes"+expires+"; path=/";
        $(this).parent().hide();
    });
    
    var $location_edit = $('.googleMapEdit, .geolocation_wrapper.edit');
    var $pleiades_url = $('input#form-widgets-IGeolocationBehavior-pleiades_url, input#form-widgets-pleiades_url, input#pleiadesUrl');
    if ($location_edit.length) {
        var $pleiades_widget = $('<button class="PleiadesFetch">Fetch</button>');
        $pleiades_url.after($pleiades_widget);
        $pleiades_widget.on('click',
            function (e) {
                e.preventDefault();
                e.stopPropagation();
                var $input = $(this).siblings('input');
                var url = $input.val();
                $.getJSON(url,
                    function (data) {
                        if (!data) {
                            window.alert('No data found in response');
                        }
                        if ($('body').hasClass('template-isaw-policy-location') || $('body').hasClass('portaltype-isaw-policy-location')) {
                            if (data.title) {
                                $('input#form-widgets-IDublinCore-title').val(data.title);
                            }
                            if (data.description) {
                                $('textarea#form-widgets-IDublinCore-description').val(data.description);
                            }
                        }
                        var repr_point = data.reprPoint;
                        if (repr_point) {
                            $location_edit.find('input#geolocation_latitude, input.geolocationfield-field.latitude').val(repr_point[1]);
                            $location_edit.find('input#geolocation_longitude, input.geolocationfield-field.longitude').val(repr_point[0]).trigger('change');
                        } else {
                            window.alert('No representative point found in response');
                        }
                    }
                ).error(function () {window.alert('Error fetching ' + url);});
                return false;
            }
        );
    }

    var $lat = $('input.geolocation-widget.latitude, input#geolocation_latitude');
    if ($lat.length) {
        $lat.wrap('<div />').parent().prepend('<label for="'+$lat.attr('id')+'">latitude:</label> ');
    }
    var $long = $('input.geolocation-widget.longitude, input#geolocation_longitude');
    if ($long.length) {
        $long.wrap('<div />').parent().prepend('<label for="'+$long.attr('id')+'">longitude:</label> ');
    }

    L.Icon.Default.imagePath = '++resource++plone.formwidget.geolocation/images';

    var _initialize_map = function (el) {
        var map, bounds, baseLayers, map_wrap, editable, markers, geosearch;

        map_wrap = $(el).closest('div.geolocation_wrapper');
        editable = map_wrap.hasClass('edit');

        var update_inputs = function(lat, lng) {
          map_wrap.find('input.latitude').attr('value', lat);
          map_wrap.find('input.longitude').attr('value', lng);
        };

        var bind_draggable_marker = function (marker) {
          marker.on('dragend', function(e) {
            var coords = e.target.getLatLng();
            update_inputs(coords.lat, coords.lng);
          });
        };

        // Default marker
        var green_marker = L.AwesomeMarkers.icon({
          markerColor: 'green'
        });

        var primary_markers = function (geopoints, editable) {
            // return MarkerClusterGroup from geopoints
            // geopoints = [{lat: NUMBER, lng: NUMBER, popup: STRING}]
            var markers = new L.MarkerClusterGroup();
            for(var i = 0, size = geopoints.length; i < size ; i++){
              var geopoint = geopoints[i],
                  marker;
              marker = new L.Marker([geopoint.lat, geopoint.lng], {
                icon: green_marker,
                draggable: editable
              });
              if (geopoint.popup) {
                marker.bindPopup(geopoint.popup);
              }
              if (editable) {
                bind_draggable_marker(marker);
              }
              markers.addLayer(marker);
            }
            return markers;
        };

        var folder_markers = function (el) {
            var markers = new L.MarkerClusterGroup();
            var $items = $(el).children("ul").children('li');

            $items.each(function (i, e) {
                var $node = $(e);
                var $geo = $node.find('.geo');
                var marker = new L.Marker([$geo.find('.latitude').text(),
                                           $geo.find('.longitude').text()],
                                          {icon: green_marker, draggable: false});
                var $wrapper = $('<div />');
                $node.find('.title').clone().appendTo($wrapper);
                $node.find('.tab').clone().appendTo($wrapper);

                var $tabs = $wrapper.find('.tab');
                // create tabs
                if ($tabs.length > 1){
                    var $handlers = $('<div class="infowindowTabHandlers" />');

                    $tabs.each(function (){
                        var $this = $(this);
                        var title = $this.attr('title');
                        var $handler = $('<div class="infowindowTabHandler">' + title + '</div>').click(function (){
                            $tabs.not($this).hide();
                            $this.show();
                            $(this).addClass('selected').siblings().removeClass('selected');
                        });
                        $handlers.append($handler);
                    });
                    $handlers.find('.infowindowTabHandler').eq(0).click();
                    $wrapper.prepend($handlers);
                }

                marker.bindPopup($wrapper.get(0));
                markers.addLayer(marker);
            });
            return markers;
        };

        map = new L.Map(el, {
            fullscreenControl: true, attributionControl: false
        });
        L.control.attribution({prefix: false, position: 'bottomright'}).addTo(map);

        // Layers
        baseLayers = {
            'Terrain': L.tileLayer(
                'https://api.tiles.mapbox.com/v4/isawnyu.map-knmctlkh/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiaXNhd255dSIsImEiOiJBWEh1dUZZIn0.SiiexWxHHESIegSmW8wedQ',
                {attribution: 'Powered by <a href="http://leafletjs.com/">Leaflet</a> and <a href="https://www.mapbox.com/">Mapbox</a>. Map base by <a title="Ancient World Mapping Center (UNC-CH)" href="http://awmc.unc.edu">AWMC</a>, 2014 (cc-by-nc).',
                 maxZoom: 12}
            ),
            'Streets': L.tileLayer(
                'https://api.tiles.mapbox.com/v4/isawnyu.map-zr78g89o/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiaXNhd255dSIsImEiOiJBWEh1dUZZIn0.SiiexWxHHESIegSmW8wedQ',
                {attribution: 'Powered by <a href="http://leafletjs.com/">Leaflet</a> and <a href="https://www.mapbox.com/">Mapbox</a>. Map base by <a title="Institute for the Study of the Ancient World (ISAW)" href="http://isaw.nyu.edu">ISAW</a>, 2014 (cc-by).'}
            )
            //'Watercolor': L.tileLayer.provider('Stamen.Watercolor')
        };

        baseLayers.Terrain.addTo(map);
        L.control.layers(baseLayers).addTo(map);

        // ADD MARKERS
        var geopoints = $(el).data().geopoints;
        if (geopoints) {
            markers = primary_markers(geopoints, editable);
        } else {
            markers = folder_markers(el);
        }
        map.addLayer(markers);

        // autozoom
        bounds = markers.getBounds();
        map.fitBounds(bounds.pad(0.05));
        if (editable) {
            map.on('geosearch_showlocation', function(e) {
                map.removeLayer(markers);
                var coords = e.Location;
                update_inputs(coords.Y, coords.X);
                bind_draggable_marker(e.Marker);
            });

            // GEOSEARCH
            geosearch = new L.Control.GeoSearch({
                showMarker: true,
              draggable: editable,
                provider: new L.GeoSearch.Provider.Esri()
            });
            geosearch.addTo(map);

            // Follow manual changes
            map_wrap.find('input#geolocation_latitude, input.geolocationfield-field.latitude, input#geolocation_longitude, input.geolocationfield-field.longitude').on('change', function () {
                map.removeLayer(markers);
                var lng = map_wrap.find('input#geolocation_longitude, input.geolocationfield-field.longitude').val();
                var lat = map_wrap.find('input#geolocation_latitude, input.geolocationfield-field.latitude').val();
                markers = primary_markers([{lat: lat, lng: lng}], editable);
                map.addLayer(markers);
                map.fitBounds(markers.getBounds());
            });
        }
    };

    var initialize_map =  function() {
        $('.folder-map, .map').each(function () {
            _initialize_map(this);
        });
    };

    $(document).ready(initialize_map);

    // Truncate breadcrumbs
    var $breadcrumbs = $('#portal-breadcrumbs > span');
    $breadcrumbs.each(function () {
        var $breadcrumb = $(this);
        var $link = $breadcrumb.find('a');
        $breadcrumb = $link.length ? $link : $breadcrumb;
        var text = $breadcrumb.text().split(':')[0].trim();
        if (text.length > 50) {
            text = text.substr(0,50).split(" ").slice(0, -1).join(" ") + '\u2026'
        }
        $breadcrumb.text(text);
    });

    // Publication or news edit form bling
    var $people_widgets = [];
    var $pub_edit_form = $('body.template-edit.portaltype-isaw-policy-publication #content-core form, body.template-isaw-policy-publication #content-core form');
    var $news_edit_form = $('body.template-atct_edit.portaltype-news-item #content form');
    if ($pub_edit_form.length) {
        $people_widgets = $pub_edit_form.find('#formfield-form-widgets-authors, #formfield-form-widgets-editors, #formfield-form-widgets-contributors');
    }
    if ($news_edit_form.length) {
        $people_widgets = $news_edit_form.find('#archetypes-fieldname-creators, #archetypes-fieldname-contributors');
    }
    if ($people_widgets.length) {
        $.getJSON('isaw-users.json').done(function (data) {
            var $select = $('<select><option value=""></option></select>');
            for (var val in data) {
                val = data[val];
                $("<option />", {value: val.id, text: val.name + ' (' + val.id +')'}).appendTo($select);
            }
            $people_widgets.each(function () {
                var $this = $(this);
                var $field = $this.find('textarea');
                var $widget = $select.clone();
                $this.append($widget);
                $widget.change(function () {
                    var id = $widget.val();
                    if (!id) { return; }
                    var val = $field.val();
                    if (val) { val = val + '\n'; }
                    $field.val(val + id);
                    $widget.val('');
                });
            });
        });
    }
});
