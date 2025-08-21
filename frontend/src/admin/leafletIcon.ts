import L from 'leaflet';
import iconUrl from '/marker-icon.png';
import shadowUrl from '/marker-shadow.png';
import iconRetinaUrl from '/marker-icon-2x.png';

export const defaultIcon = L.icon({
  iconUrl,
  shadowUrl,
  iconRetinaUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41],
});
