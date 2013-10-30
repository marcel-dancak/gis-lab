#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Ivan Mincik, ivan.mincik@gmail.com
"""

import sys
from cgi import parse_qsl
from optparse import OptionParser
from owslib.wms import WebMapService


DEBUG=True
COMMAND_LINE_MODE=False

def _get_resolutions(scales, units, resolution=96):
	"""Helper function to compute OpenLayers resolutions."""

	resolution = float(resolution)
	factor = {'in': 1.0, 'ft': 12.0, 'mi': 63360.0,
			'm': 39.3701, 'km': 39370.1, 'dd': 4374754.0}
	
	inches = 1.0 / resolution
	monitor_l = inches / factor[units]
	
	resolutions = []
	for m in scales:
		resolutions.append(monitor_l * int(m))
	return resolutions


def page(c):
	"""Return viewer application HTML code."""

	html = ''

	c['static_url_prefix'] = 'https://rawgithub.com/imincik/gis-lab/master/system/wms-viewer/' if COMMAND_LINE_MODE else ''

	# head and javascript start
	html += """
	<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

        <link rel="stylesheet" type="text/css" href="%(static_url_prefix)sstatic/ext-3.4.1/resources/css/ext-all.css"/>

        <script type="text/javascript" src="%(static_url_prefix)sstatic/ext-3.4.1/adapter/ext/ext-base.js"></script>
        <script type="text/javascript" src="%(static_url_prefix)sstatic/ext-3.4.1/ext-all.js"></script>

        <script type="text/javascript" src="%(static_url_prefix)sstatic/OpenLayers-2.13/OpenLayers.js"></script>
        <script type="text/javascript" src="%(static_url_prefix)sstatic/GeoExt-1.1/GeoExt.js"></script>

        <style type="text/css">
             .olControlNoSelect {background-color:rgba(200, 200, 200, 0.3)}
              #dpiDetection {height: 1in; left: -100%%; position: absolute; top: -100%%; width: 1in;}

            .x-panel-header {
                color: #15428B;
                font-family: tahoma,arial,verdana,sans-serif;
                font-size: 11px;
                font-weight: bold;
            }
            .x-panel-body-text {
                font-family: tahoma,arial,verdana,sans-serif;
                font-size: 11px;
            }
            .home-icon {
                background-image: url('%(static_url_prefix)sstatic/images/toolbar/home.png')!important;
                background: no-repeat;
            }
            .pan-icon {
                background-image: url('%(static_url_prefix)sstatic/images/toolbar/pan.png')!important;
                background: no-repeat;
            }
            .zoom-in-icon {
                background-image: url('%(static_url_prefix)sstatic/images/toolbar/zoom_in.png')!important;
                background: no-repeat;
            }
            .zoom-out-icon {
                background-image: url('%(static_url_prefix)sstatic/images/toolbar/zoom_out.png')!important;
                background: no-repeat;
            }
            .zoom-max-extent-icon {
                background-image: url('%(static_url_prefix)sstatic/images/toolbar/arrow_out.png')!important;
                background: no-repeat;
            }
            .previous-icon {
                background-image: url('%(static_url_prefix)sstatic/images/toolbar/arrow_left.png')!important;
                background: no-repeat;
            }
            .next-icon {
                background-image: url('%(static_url_prefix)sstatic/images/toolbar/arrow_right.png')!important;
                background: no-repeat;
            }
            .length-measure-icon {
                background-image: url('%(static_url_prefix)sstatic/images/toolbar/ruler.png')!important;
                background: no-repeat;
            }
            .area-measure-icon {
                background-image: url('%(static_url_prefix)sstatic/images/toolbar/ruler_square.png')!important;
                background: no-repeat;
            }
        </style>

        <title id="page-title">%(root_title)s</title>
        <script type="text/javascript">
	""" % c


	# configuration
	html += """function main() {
		Ext.BLANK_IMAGE_URL = "%(static_url_prefix)sstatic/images/s.gif";
		OpenLayers.DOTS_PER_INCH = %(resolution)s;
		var config = {
			projection: "%(projection)s",
			units: "%(units)s",
			resolutions: [%(resolutions)s],
			maxExtent: [%(extent)s],
		};

		var x = %(center_coord1)s;
		var y = %(center_coord2)s;
		var zoom = %(zoom)s;
		var layer = null;

	""" % c

	if DEBUG: html += """console.log("CONFIG: %s");""" % c

	# layers
	html += "var maplayers = ["
	for lay in c['layers']:
		html += """
		new OpenLayers.Layer.WMS(
		"%s",
		["%s&TRANSPARENT=TRUE"],
		{
			layers: "%s",
			format: "%s",
		},
		{
			gutter: 0,
			isBaseLayer: false,
			buffer: 0,
			visibility: true,
			singleTile: true,
			// attribution: "",
		}
	),
	""" % (lay, c['ows_url'], lay, 'image/png')

	if c['osm']:
		html += "new OpenLayers.Layer.OSM(),"

	html += "];"

	# map panel
	if c['osm']:
		c['allOverlays'] = 'false'
	else:
		c['allOverlays'] = 'true'
	html += """
		var ctrl, action;
		var mappanel = new GeoExt.MapPanel({
			region: 'center',
			title: '%(root_title)s',
			collapsible: false,
			zoom: 3,
			map: {
				allOverlays: %(allOverlays)s,
				units: config.units,
				projection: new OpenLayers.Projection(config.projection),
				resolutions: config.resolutions,
				maxExtent: new OpenLayers.Bounds(config.maxExtent[0], config.maxExtent[1],
					config.maxExtent[2], config.maxExtent[3]),
				controls: []
			},
			layers: maplayers,
			tbar: [],
			bbar: []
		});

		//Home Action
		action = new GeoExt.Action({
			handler: function() {window.location.reload();},
			map: mappanel.map,
			cls: 'x-btn-icon',
			iconCls: 'home-icon',
			tooltip: 'Home'
		});
		mappanel.getTopToolbar().add('-', action);

		//Pan Map Action
		action = new GeoExt.Action({
			control: new OpenLayers.Control.MousePosition({formatOutput: function(lonLat) {return '';}}),
			map: mappanel.map,
			toggleGroup: 'tools',
			group: 'tools',
			cls: 'x-btn-icon',
			iconCls: 'pan-icon',
			tooltip: 'Pan'
		});
		mappanel.getTopToolbar().add(action);

		//Zoom In Action
		action = new GeoExt.Action({
			control: new OpenLayers.Control.ZoomBox({alwaysZoom:true}),
			map: mappanel.map,
			toggleGroup: 'tools',
			group: 'tools',
			cls: 'x-btn-icon',
			iconCls: 'zoom-in-icon',
			tooltip: 'Zoom In'
		});
		mappanel.getTopToolbar().add(action);

		//Zoom Out Action
		action = new GeoExt.Action({
			control: new OpenLayers.Control.ZoomBox({alwaysZoom:true, out:true}),
			map: mappanel.map,
			toggleGroup: 'tools',
			group: 'tools',
			cls: 'x-btn-icon',
			iconCls: 'zoom-out-icon',
			tooltip: 'Zoom Out',
		});
		mappanel.getTopToolbar().add(action);

		// ZoomToMaxExtent control, a 'button' control
		action = new GeoExt.Action({
			control: new OpenLayers.Control.ZoomToMaxExtent(),
			map: mappanel.map,
			cls: 'x-btn-icon',
			iconCls: 'zoom-max-extent-icon',
			tooltip: 'Zoom to max extent'
		});
		mappanel.getTopToolbar().add(action, '-');

		// Navigation history - two 'button' controls
		ctrl = new OpenLayers.Control.NavigationHistory();
		mappanel.map.addControl(ctrl);

		action = new GeoExt.Action({
			control: ctrl.previous,
			disabled: true,
			cls: 'x-btn-icon',
			iconCls: 'previous-icon',
			tooltip: 'Previous in history',
		});
		mappanel.getTopToolbar().add(action);

		action = new GeoExt.Action({
			control: ctrl.next,
			disabled: true,
			cls: 'x-btn-icon',
			iconCls: 'next-icon',
			tooltip: 'Next in history',
		});
		mappanel.getTopToolbar().add(action, '-');

		var length = new OpenLayers.Control.Measure(OpenLayers.Handler.Path, {
			immediate: true,
			persist: true,
			geodesic: true, //only for projected projections
			eventListeners: {
				measurepartial: function(evt) {
					Ext.getCmp('measurement-info').setText('Length: ' + evt.measure.toFixed(2) + evt.units);
				},
				measure: function(evt) {
					Ext.getCmp('measurement-info').setText('Length: ' + evt.measure.toFixed(2) + evt.units);
				}
			}
		});

		var area = new OpenLayers.Control.Measure(OpenLayers.Handler.Polygon, {
			immediate: true,
			persist: true,
			geodesic: true, //only for projected projections
			eventListeners: {
				measurepartial: function(evt) {
					Ext.getCmp('measurement-info').setText('Area: ' + evt.measure.toFixed(2) + evt.units + '<sup>2</sup>');
				},
				measure: function(evt) {
					Ext.getCmp('measurement-info').setText('Area: ' + evt.measure.toFixed(2) + evt.units + '<sup>2</sup>');
				}
			}
		});

		mappanel.map.addControl(length);
		mappanel.map.addControl(area);

		var length_button = new Ext.Button({
			enableToggle: true,
			toggleGroup: 'tools',
			iconCls: 'length-measure-icon',
			toggleHandler: function(button, toggled) {
				if (toggled) {
					length.activate();
				} else {
					length.deactivate();
					Ext.getCmp('measurement-info').setText('');
				}
			}
		});

		var area_button = new Ext.Button({
			enableToggle: true,
			toggleGroup: 'tools',
			iconCls: 'area-measure-icon',
			toggleHandler: function(button, toggled) {
				if (toggled) {
					area.activate();
				} else {
					area.deactivate();
					Ext.getCmp('measurement-info').setText('');
				}
			}
		});
		mappanel.getTopToolbar().add(length_button, area_button);
	""" % c

	# tree node
	html += """
			var layers_root = new Ext.tree.TreeNode({
				text: 'Layers',
				expanded: true,
				draggable: false
			});
	"""

	# base layers tree
	if c['osm']:
		html += """
			layers_root.appendChild(new GeoExt.tree.BaseLayerContainer({
				text: 'Base Layers',
				map: mappanel.map,
				leaf: false,
				expanded: true,
				draggable: false,
				isTarget: false,
				split: true
			}));
		"""

	# overlay layers tree
	html += """
			layers_root.appendChild(new GeoExt.tree.OverlayLayerContainer({
				text: 'Overlays',
				map: mappanel.map,
				leaf: false,
				expanded: true,
				draggable: false,
				autoScroll: true,
			}));
	"""

	# layers tree
	html += """
			var layer_treepanel = new Ext.tree.TreePanel({
				title: 'Content',
				enableDD: true,
				root: layers_root,
				split: true,
				border: true,
				collapsible: false,
				cmargins: '0 0 0 0',
				autoScroll: true
			});
	"""

	# legend
	html += """
		var layer_legend = new GeoExt.LegendPanel({
			title: 'Legend',
			map: mappanel.map,
			border: false,
			ascending: false,
			autoScroll: true,
			defaults: {
				cls: 'legend-item',
				baseParams: {
					FORMAT: 'image/png',
					LEGEND_OPTIONS: 'forceLabels:on'
				}
			}
		});
	"""

	# properties
	html += """
			var properties = new Ext.Panel({
				title: 'Properties',
				autoScroll: true,
				html: '<div class="x-panel-body-text"><p><b>Author: </b>%(author)s</p><p><b>E-mail: </b>%(email)s</p><p><b>Organization: </b>%(organization)s</p><b>Abstract: </b>%(abstract)s</p></div>'
			});
	""" % c

	# legend and properties accordion panel
	html += """
			var accordion = new Ext.Panel({
				layout: {
					type: 'accordion',
					titleCollapse: true,
					animate: false,
					activeOnTop: false
				},
				items: [
					layer_legend,
					properties
				]
			});
	"""

	# left panel
	html += """
			var left_panel = new Ext.Panel({
				region: 'west',
				width: 200,
				defaults: {
					width: '100%',
					flex: 1
				},
				layout: 'vbox',
				collapsible: true,
				layoutConfig: {
					align: 'stretch',
					pack: 'start'
				},
				items: [
					layer_treepanel,
					accordion
				]
			});
	"""

	#featureinfo panel
	html += """
			var featureinfo_panel = new Ext.Panel({
				title: 'Feature Info',
				collapsible: true,
				region: 'south'
			});
	"""

	html += """
			var mappanel_container = new Ext.Panel({
				layout: 'border',
				region: 'center',
				items: [
					mappanel,
					featureinfo_panel
				]
			});
	"""

	# viewport
	html += """
			var webgis = new Ext.Viewport({
				layout: "border",
				items: [
					mappanel_container,
					left_panel
				]
			});
	"""

	# controls
	html += """
			Ext.namespace("GeoExt.Toolbar");

			GeoExt.Toolbar.ControlDisplay = Ext.extend(Ext.Toolbar.TextItem, {

				control: null,
				map: null,

				onRender: function(ct, position) {
					this.text = this.text ? this.text : '&nbsp;';

					GeoExt.Toolbar.ControlDisplay.superclass.onRender.call(this, ct, position);
					this.control.div = this.el.dom;

					if (!this.control.map && this.map) {
						this.map.addControl(this.control);
					}
				}
			});
			var coords = new GeoExt.Toolbar.ControlDisplay({control: new OpenLayers.Control.MousePosition({separator: ' , '}), map: mappanel.map});

			mappanel.getBottomToolbar().add(new Ext.Toolbar.TextItem({text: config.projection}));
			mappanel.getBottomToolbar().add(' ', '-', '');
			mappanel.getBottomToolbar().add(coords);
			var measurement_output = new Ext.Toolbar.TextItem({
				id:'measurement-info',
				text: ''
			});
			mappanel.getBottomToolbar().add(' ', '-', ' ', measurement_output);

			mappanel.map.setCenter(new OpenLayers.LonLat(%(center_coord1)s, %(center_coord2)s), %(zoom)s);
			mappanel.map.addControl(new OpenLayers.Control.Scale());
			mappanel.map.addControl(new OpenLayers.Control.ScaleLine());
			mappanel.map.addControl(new OpenLayers.Control.PanZoomBar());
			mappanel.map.addControl(new OpenLayers.Control.Navigation());
			mappanel.map.addControl(new OpenLayers.Control.Attribution());
		};
	""" % c

	html += """
		Ext.QuickTips.init();
		Ext.onReady(main);
				</script>
			</head>
			<body>
				<div id="overviewLegend" style="margin-left:10px"></div>
				<div id="dpiDetection"></div>
			</body>
		</html>
	"""

	return html


def application(environ, start_response):
	"""Return server response."""

	OWS_URL="http://192.168.50.5/cgi-bin/qgis_mapserv.fcgi" #  TODO: do not hardcode this
	DEFAULT_SCALES="1000000,500000,250000,100000,50000,25000,10000,5000,2500,1000,500"
	PROJECTION_UNITS_DD=('EPSG:4326',)

	qs = dict(parse_qsl(environ['QUERY_STRING'])) # collect GET parameters
	qs = dict((k.upper(), v) for k, v in qs.iteritems()) # change GET parameters names to uppercase

	try:
		projectfile = '/storage/share/' + qs.get('PROJECT') # TODO: use Apache rewrite
		getcapabilities_url = "{0}/?map={1}&REQUEST=GetCapabilities".format(OWS_URL, projectfile)

		wms_service = WebMapService(getcapabilities_url, version="1.1.1") # read WMS GetCapabilities
	except:
		start_response('404 NOT FOUND', [('content-type', 'text/plain')])
		return ('Project file does not exist or it is not accessible.',)

	root_layer = None
	for layer in wms_service.contents.itervalues():
		if not layer.parent:
			root_layer = layer
			break
	if not root_layer: raise Exception("Root layer not found.")

	extent = root_layer.boundingBox[:-1]

	# set some parameters from GET request (can override parameters from WMS GetCapabilities)
	if qs.get('DPI'):
		resolution = qs.get('DPI')
	else:
		resolution = 96

	if qs.get('SCALES'):
		scales = map(int, qs.get('SCALES').split(","))
	else:
		scales = map(int, DEFAULT_SCALES.split(","))

	if qs.get('ZOOM'):
		zoom = qs.get('ZOOM')
	else:
		zoom = 0

	if qs.get('CENTER'):
		center_coord1 = qs.get('CENTER').split(',')[0]
		center_coord2 = qs.get('CENTER').split(',')[1]
	else:
		center_coord1 = (extent[0]+extent[2])/2.0
		center_coord2 = (extent[1]+extent[3])/2.0


	if qs.get('LAYERS'):
		layers_names = qs.get('LAYERS').split(',')
	else:
		layers_names = [layer.name.encode('UTF-8') for layer in root_layer.layers][::-1]

	c = {} # configuration dictionary which will be used in HTML template
	c['projectfile'] = projectfile
	c['projection'] = root_layer.boundingBox[-1]

	if c['projection'] in PROJECTION_UNITS_DD: # TODO: this is very naive
		c['units'] = 'dd'
	else:
		c['units'] = 'm'

	if qs.get('OSM') in ('true', 'TRUE', 'True') and c['projection'] == 'EPSG:3857':
		c['osm'] = True
	else:
		c['osm'] = False
	
	c['resolution'] = resolution
	c['extent'] = ",".join(map(str, extent))
	c['center_coord1'] = center_coord1
	c['center_coord2'] = center_coord2
	c['scales'] = scales
	c['zoom'] = zoom
	c['resolutions'] = ', '.join(str(r) for r in _get_resolutions(c['scales'], c['units'], c['resolution']))
	c['author'] = wms_service.provider.contact.name.encode('UTF-8')
	c['email'] = wms_service.provider.contact.email.encode('UTF-8')
	c['organization'] = wms_service.provider.contact.organization.encode('UTF-8')
	c['abstract'] = wms_service.identification.abstract.encode('UTF-8')

	c['root_layer'] = root_layer.name.encode('UTF-8')
	c['root_title'] = wms_service.identification.title.encode('UTF-8')
	c['layers'] = layers_names
	c['ows_url'] = '{0}/?map={1}&DPI={2}'.format(OWS_URL, projectfile, resolution)
	c['ows_get_capabilities_url'] = getcapabilities_url

	start_response('200 OK', [('Content-type','text/html')])
	return page(c)


def run(port=9997):
	"""Start WSGI server."""

	from wsgiref import simple_server
	httpd = simple_server.WSGIServer(('', port), simple_server.WSGIRequestHandler,)
	httpd.set_app(application)
	try:
		print "Starting server. Point your web browser to 'http://127.0.0.1:%s'." % port
		httpd.serve_forever()
	except KeyboardInterrupt:
		print "Shutting down server."
		sys.exit(0)


if __name__ == "__main__":
	parser = OptionParser()

	parser.add_option("-p", "--port", help="port to run server on [optional]",
		dest="port", action='store', type="int", default=9991)

	options, args = parser.parse_args()
	COMMAND_LINE_MODE = True
	run(options.port)


# vim: set ts=4 sts=4 sw=4 noet:
