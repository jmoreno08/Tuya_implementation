import time
import hmac
import hashlib
import json
from typing import Any, Dict, Optional, List
from urllib.parse import quote, urlencode

import requests

class TuyaClient:
    """Cliente Python para la API Cloud de Tuya."""

    def __init__(self, client_id: str, secret: str, base_url: str) -> None:
        self.client_id = client_id
        self.secret = secret
        self.base_url = base_url.rstrip("/")
        self.access_token: Optional[str] = None
        self.session = requests.Session()

    # ---------- Helpers ----------
    @staticmethod
    def _sha256(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _now_ms() -> str:
        return str(int(time.time() * 1000))

    @staticmethod
    def _canonical_url(path: str, query: Optional[Dict[str, Any] | List] = None) -> str:
        if not path.startswith("/"):
            path = "/" + path

        items = list(query.items()) if isinstance(query, dict) else (list(query) if query else [])
        items.sort(key=lambda kv: kv[0])

        q = "&".join(
            f"{quote(str(k), safe='')}={quote('' if v is None else str(v), safe='')}"
            for k, v in items
        )
        return f"{path}?{q}" if q else path

    @staticmethod
    def _normalize_body(body: Any, headers: Optional[Dict[str, str]]) -> str:
        if not body:
            return ""

        ct = (headers or {}).get("Content-Type", "").lower()
        if "application/json" in ct:
            return body if isinstance(body, str) else json.dumps(body, separators=(",", ":"), ensure_ascii=False)
        if "application/x-www-form-urlencoded" in ct:
            return urlencode(body, doseq=True) if isinstance(body, (dict, list, tuple)) else str(body)

        return ""  # multipart/otros

    def _string_to_sign(
        self, method: str, url: str, body_str: str, headers: Optional[Dict[str, str]], sig_headers: Optional[List[str]]
    ) -> str:
        hdr_block = "".join(f"{k}:{headers.get(k, '')}\n" for k in (sig_headers or []))
        return f"{method.upper()}\n{self._sha256(body_str)}\n{hdr_block}\n{url}"

    def _hmac_sha256_upper(self, text: str) -> str:
        return hmac.new(self.secret.encode(), text.encode(), hashlib.sha256).hexdigest().upper()

    # ---------- Token ----------
    def get_token(self, grant_type: int = 1, nonce: str = "") -> Dict[str, Any]:
        path, query = "/v1.0/token", {"grant_type": str(grant_type)}
        t = self._now_ms()
        canonical = self._canonical_url(path, query)
        s2s = self._string_to_sign("GET", canonical, "", None, None)

        sign = self._hmac_sha256_upper(self.client_id + t + (nonce or "") + s2s)
        headers = {
            "client_id": self.client_id,
            "t": t,
            "sign": sign,
            "sign_method": "HMAC-SHA256",
        }
        if nonce:
            headers["nonce"] = nonce

        response = self.session.get(self.base_url + canonical, headers=headers)
        data = response.json()

        if data.get("success") and data.get("result", {}).get("access_token"):
            self.access_token = data["result"]["access_token"]

        return data

    # ---------- Requests ----------
    def request(
        self,
        method: str,
        path: str,
        *,
        query: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Any = None,
        sig_headers: Optional[List[str]] = None,
        nonce: str = "",
    ) -> requests.Response:
        if not self.access_token:
            raise RuntimeError("Debes llamar primero a get_token().")

        headers = dict(headers or {})
        body_str = self._normalize_body(body, headers)
        canonical = self._canonical_url(path, query)
        s2s = self._string_to_sign(method, canonical, body_str, headers, sig_headers)

        t = self._now_ms()
        sign = self._hmac_sha256_upper(self.client_id + self.access_token + t + (nonce or "") + s2s)

        signed_headers = {
            "client_id": self.client_id,
            "t": t,
            "sign": sign,
            "sign_method": "HMAC-SHA256",
            "access_token": self.access_token,
        }
        if nonce:
            signed_headers["nonce"] = nonce
        if sig_headers:
            signed_headers["Signature-Headers"] = ":".join(sig_headers)

        signed_headers.update({k: v for k, v in headers.items() if k not in signed_headers})

        url = self.base_url + canonical
        return self.session.request(method.upper(), url, headers=signed_headers, data=body_str.encode())
