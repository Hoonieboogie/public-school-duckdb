"""Standalone API test — no project imports, just raw HTTP call.

Run: python test.py
"""

import json
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SCHOOLINFO_API_KEY", "")
BASE_URL = "https://www.schoolinfo.go.kr/openApi.do"

resp = httpx.get(BASE_URL, params={
    "apiKey": API_KEY,
    "apiType": "0",
    "sidoCode": "11",
    "sggCode": "11140",
    "schulKndCode": "02",
})

body = resp.json()

print(f"Status: {resp.status_code}")
print(f"resultCode: {body.get('resultCode')}")
print(f"resultMsg: {body.get('resultMsg')}")
print(f"Total rows: {len(body.get('list', []))}\n")

print("=== First record ===")
print(json.dumps(body["list"][0], indent=2, ensure_ascii=False))

print(f"\n=== All keys ({len(body['list'][0])} fields) ===")
for k, v in body["list"][0].items():
    print(f"  {k:30s} : {v}")

print()
