#!/usr/bin/env python3
# fill_stats_location.py
# Atualiza documentos em collection stats_access usando GeoLite2-City.mmdb

import os
from pymongo import MongoClient
import geoip2.database

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
# Fallback para o arquivo mmdb no mesmo diretório 'backend'
MMDB_PATH = os.environ.get("GEOIP_DB_PATH") or os.path.abspath(os.path.join(os.path.dirname(__file__), 'GeoLite2-City.mmdb'))

client = MongoClient(MONGO_URL)
db = client['equora']
col = db['stats_access']

print("MMDB path:", MMDB_PATH)
if not os.path.exists(MMDB_PATH):
    raise SystemExit("MMDB não encontrado em: " + MMDB_PATH)

updated = 0
with geoip2.database.Reader(MMDB_PATH) as reader:
    # cursor para documentos sem location ou com lat/lon como string
    cursor = col.find({
        "$or": [
            {"location": {"$exists": False}},
            {"location.latitude": {"$type": "string"}},
            {"location.longitude": {"$type": "string"}}
        ]
    })
    for doc in cursor:
        ip = doc.get("ip")
        if not ip:
            continue
        try:
            res = reader.city(ip)
            if res and res.location and res.location.latitude is not None and res.location.longitude is not None:
                loc = {
                    "country": res.country.name,
                    "city": res.city.name,
                    "latitude": float(res.location.latitude),
                    "longitude": float(res.location.longitude)
                }
                col.update_one({"_id": doc["_id"]}, {"$set": {"location": loc}})
                updated += 1
                print("Updated", doc["_id"], ip, loc)
        except Exception as e:
            # ip privado ou não resolvido
            print("Skip", doc.get("_id"), ip, "->", repr(e))
print("Total updated:", updated)