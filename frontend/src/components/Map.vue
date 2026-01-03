<script setup lang="ts">
import { onMounted, useTemplateRef } from "vue";

import FindMyWeb, { Accessory, Location, BasicLocation, BatteryLevel } from "../lib/FindMyWeb.ts";
import { locationDateString } from "../lib/helpers.ts";

import "maplibre-gl/dist/maplibre-gl.css";
import maplibregl from "maplibre-gl";

import { loadIcon } from "@iconify/vue";

const mapdiv = useTemplateRef("mapdiv");
const FindMyWebAPI = new FindMyWeb();

let map: maplibregl.Map | null;
let popups: maplibregl.Popup[] = [];
let markers: maplibregl.Marker[] = [];

const mapObserver = new ResizeObserver(() => {
    if (map) {
        map.resize();
    }
});

async function b64Char(inp: number) : Promise<string> {
  return "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"[inp];
}

async function urlsafeString(inp: string): Promise<string> {
  return inp.replace(/[^a-z0-9]/gi, '_');
}

async function coMapsUri(name: string, location: Location): Promise<string> {
  if(!location.lat || !location.lon) {
    return "https://en.wikipedia.org/wiki/HTTP_404";
  }

  let charStr = "";

  const maxCoordBits = 10*3;

  const maxValue = (1 << maxCoordBits) - 1;

  const zoomI = 8;

  charStr += await b64Char(zoomI);


  const latX = (location.lat + 90.0) / 180.0 * maxValue;
  const lat = latX < 0 ? 0 : (latX > maxValue ? maxValue : Math.round(latX));

  const lonX = (location.lon + 180.0) / 360.0 * (maxValue + 1.0) + 0.5;
  const lon = (lonX <= 0 || lonX >= maxValue + 1) ? 0 : lonX;

  for (let i = 0, shift = maxCoordBits - 3; i < 9; ++i, shift -= 3)
    {
      const latBits = lat >> shift & 7;
      const lonBits = lon >> shift & 7;

      const nextByte =
        (latBits >> 2 & 1) << 5 |
        (lonBits >> 2 & 1) << 4 |
        (latBits >> 1 & 1) << 3 |
        (lonBits >> 1 & 1) << 2 |
        (latBits      & 1) << 1 |
        (lonBits      & 1);

      charStr += await b64Char(nextByte);
    }

  return `https://comaps.at/${charStr}/${await urlsafeString(name)}`;
}

// @ts-ignore: Name can't be set in a geoUri
async function geoUri(name: string, location: Location): Promise<string> {
  if(!location.lat || !location.lon) {
    return "https://en.wikipedia.org/wiki/HTTP_404";
  }
  return `geo:${location.lat},${location.lon};crs=wgs84;u=0`;

}

async function appleMaps(name: string, location: Location) {
  if(!location.lat || !location.lon) {
    return "https://en.wikipedia.org/wiki/HTTP_404";
  }
  return `https://maps.apple.com/?ll=${location.lat},${location.lon}&q=${await urlsafeString(name)}`;
}

async function getHtmlForLocation(header: string, name: string, location: Location) {
  return `<h1>
    <b>${header}</b>
    <i>(${await locationDateString(location)})</i>
    <b>:</b>
  </h1>
  <p>(${location.lat} ${location.lon})</p>
  <p>Battery: ${location.battery_level != null ? BatteryLevel[location.battery_level] : 'Not Found'}</p>
  <p>Accuracy: ${location.horizontal_accuracy != null ? `${location.horizontal_accuracy}m` : 'Not Found'}</p>
  <p>
    <u>
      <a href=${await geoUri(name, location)}>geo URI</a>
    </u>
  </p>
  <p>
    <u>
      <a target="_blank" href=${await coMapsUri(name, location)}>CoMaps</a>
    </u>
  </p>
  <p>
    <u>
      <a target="_blank" href=${await appleMaps(name, location)}>Apple Maps</a>
    </u>
  </p>`;
}


async function init() {
  map = new maplibregl.Map({
      style: "https://tiles.openfreemap.org/styles/liberty",
      center: [9.902056, 49.843],
      zoom: 3,
      container: "map",
  });
  map.addControl(
      new maplibregl.NavigationControl({
          visualizePitch: true,
          visualizeRoll: true,
          showZoom: true,
          showCompass: true,
      }),
  );
  map.scrollZoom.setWheelZoomRate(1 / 250);
  if (mapdiv.value) {
    mapObserver.observe(mapdiv.value);
  }
  await waitLoaded();
  map.setProjection({type: 'globe'});


  const circleImage = await map.loadImage("/circle-outline.png");
  const upImage = await map.loadImage("/arrow-up.png");
  map.addImage('circle-outline', circleImage.data, {sdf: true});
  map.addImage('arrow-up', upImage.data, {sdf: true});

}

async function zoomToCoordinates(lonLat: number[][], padding: number = 50) {
  if(!map){
    return;
  }

  const bounds = lonLat.reduce(
          (bounds, coord) => {
              // @ts-ignore: Works either way
              return bounds.extend(coord);
          },
          // @ts-ignore: Works either way
          new maplibregl.LngLatBounds(lonLat[0], lonLat[0]),
      );

  map.fitBounds(bounds, {
      padding: padding
    }
  );
}
async function removeLayerAndSource(name: string) {
  if(!map) {
    return;
  }

  if (map.getLayer(name)) {
    map.removeLayer(name);
  }
  if (map.getSource(name)) {
    map.removeSource(name);
  }
}
async function clear() {
  if(!map) {
    return;
  }
  await removeLayerAndSource("directionArrows");
  await removeLayerAndSource("trace");
  await removeLayerAndSource("points");
  for (var i = 0; i < markers.length; i++) {
      markers[i].remove();
  }

  for (var i = 0; i < popups.length; i++) {
      popups[i].remove();
  }
  popups = [];
  markers = [];
}

async function addLine(coordinates: number[][], color: string, name: string) {
  if(!map) {
    return;
  }

  let geoJSON = {
    type: "geojson",
    data: {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          properties: {},
          geometry: {
            type: "LineString",
            coordinates: coordinates
          },
        },
      ]
    }
  };

  // @ts-ignore: Typing geoJSON is a terrible idea
  map.addSource(name, geoJSON);
  map.addLayer({
      id: name,
      type: 'line',
      source: name,
      layout: {
          'line-join': 'bevel',
          'line-cap': 'square',
      },
      paint: {
          'line-color': color,
          'line-width': 3,
          'line-opacity': 0.3,
      }
  });


  map.addLayer({
    id: 'directionArrows',
    type: 'symbol',
    source: name,
    paint: {
      'icon-color': color,
    },
    layout: {
      'symbol-placement': 'line',
      'symbol-spacing': 1,
      'icon-allow-overlap': true,
      'icon-image': 'arrow-up',
      'icon-rotation-alignment': 'map',
      'icon-rotate': 270,
      'icon-size': 0.350,
    }
  });

}

async function addPreviousMarkers(locations: BasicLocation[], color: string, accessory_name: string, name: string) {
  if(!map) {
    return;
  }

  let geoJSON = {
    type: "geojson",
    data: {
      type: "FeatureCollection",
      features: [
      ]
    }
  };

  for (let i = 0; i < locations.length; i++ ) {
    let location = locations[i];

    if(!location.lat || !location.lon) {
      continue;
    }

    let location_text = "No timestamp";

    if (location.timestamp) {
      location_text = await locationDateString(location);
    }

    const point = {
      type: "Feature",
      properties: {
        'date': location_text,
        'location_id': location.id,
        'accessory_name': accessory_name
      },
      geometry: {
        type: "Point",
        coordinates: [location.lon, location.lat]
      },
    };

    geoJSON.data.features.push(point);
  }

  // @ts-ignore: Typing geoJSON is a terrible idea
  map.addSource(name, geoJSON);
  map.addLayer({
      id: name,
      type: 'symbol',
      source: name,
      paint: {
        'icon-color': color,
        'text-halo-color': '#EEEEEE',
        'text-halo-width': 3,
      },
      layout: {
          'icon-image': 'circle-outline',
          'icon-size': 0.25,
          'text-field': ['get', 'date'],
          'text-font': [
              'Noto Sans Regular',
          ],
          'text-overlap': 'cooperative',
          'text-offset': [0, 1.55],
          'text-anchor': 'top'
      }
  });
  map.on('click', name, async (e) => {
      if(!e.features || !map) {
        return;
      }
      // @ts-ignore: Typing geoJSON is a terrible idea
      const coordinates = e.features[0].geometry.coordinates.slice();
      const locationId = e.features[0].properties.location_id;
      const accessoryName = e.features[0].properties.accessory_name;

      const location = (await FindMyWebAPI.getLocation(accessoryName, locationId)).location;
      const description = await getHtmlForLocation("Previous", accessoryName, location);
      // Ensure that if the map is zoomed out such that multiple
      // copies of the feature are visible, the popup appears
      // over the copy being pointed to.
      while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
          coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
      }

      popups.push(new maplibregl.Popup()
          .setLngLat(coordinates)
          .setHTML(description)
          .addTo(map)
      );
  });
}

async function showMarker(accessory: Accessory, location: Location) {
  if(!map || !accessory.icon || !accessory.color || !accessory.name || !location.lat || !location.lon) {
    return;
  }

  const iconData = await loadIcon(accessory.icon);

  const element = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  element.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:xlink", "http://www.w3.org/1999/xlink");
  element.setAttribute('viewBox', `${iconData.left} ${iconData.top} ${iconData.width} ${iconData.height}`);
  element.setAttribute("class", "size-14 p-1 rounded-full border-solid border-gray-500 border-3 bg-radial from-blue-500/50 from-40% to-sky-200 to-80%");

  element.style.color = accessory.color;

  element.onclick = async (event) => {
    event.stopPropagation();
    // @ts-ignore: Properties of Accessory are always defined
    popups.push(new maplibregl.Popup({ offset: 25 }).setHTML(await getHtmlForLocation("Current", accessory.name, location)).setLngLat([location.lon, location.lat]).addTo(map));
  };

  element.innerHTML = iconData.body;

  // @ts-ignore: SVGElement is still an HTMLElement
  const marker = new maplibregl.Marker({ element: element })
            .setLngLat([location.lon, location.lat])
            .addTo(map);

  markers.push(marker);
}

async function showTrace(accessory: Accessory, locations: BasicLocation[]) {
  await clear();

  if(!locations || locations.length == 0 || !accessory.color || !accessory.name || !map) {
    return;
  }

  let coordinates = [];

  for (let i = 0; i < locations.length; i++) {

    const location = locations[i];

    coordinates.push([location.lon, location.lat]);
  }

  const lastLocationId = locations.splice(0, 1)[0].id;
  const lastLocation = (await FindMyWebAPI.getLocation(accessory.name, lastLocationId)).location;

  // @ts-ignore: Typing geoJSON is a terrible idea
  await addLine(coordinates, accessory.color, 'trace');

  await addPreviousMarkers(locations, accessory.color, accessory.name, 'points');

  await showMarker(accessory, lastLocation);

  // @ts-ignore: Typing geoJSON is a terrible idea
  await zoomToCoordinates(coordinates);

}

async function waitLoaded() {
    if(!map) {
      throw Error("Map has not been created yet");
    }
    while (!map.loaded()) {
        await new Promise((f) => setTimeout(f, 20));
    }
}

defineExpose({ showTrace, showMarker, zoomToCoordinates, clear });


onMounted(async () => {
    await init();
});



</script setup>


<template>
    <div id="map" ref="mapdiv" class="w-full h-full"></div>
</template>
