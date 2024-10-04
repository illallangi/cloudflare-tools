from yarl import URL
import requests
from requests.exceptions import RequestException
from json import JSONDecodeError


class CloudflareAccount:
    def __init__(self, api_token: str, account_id: str):
        # Validate the API token and account ID
        if not api_token:
            raise ValueError("API token is required")
        if not account_id:
            raise ValueError("Account ID is required")

        self.api_token = api_token
        self.account_id = account_id

    @property
    def headers(self) -> str:
        return {"Authorization": f"Bearer {self.api_token}"}

    def get_tunnels(self) -> list:
        try:
            # Make a GET request to the Tunnels URL with the headers
            response = requests.get(
                URL("https://api.cloudflare.com")
                / "client"
                / "v4"
                / "accounts"
                / self.account_id
                / "tunnels"
                % {"is_deleted": "false"}
                % {"tun_types": "cfd_tunnel"},
                headers=self.headers,
            )
            # Raise an exception if the request failed
            response.raise_for_status()
            # Parse the response as JSON and return it
            return [
                {
                    "_expires": response.expires.isoformat(),
                    "id": tunnel["id"],
                    "name": tunnel["name"],
                    "status": tunnel["status"],
                }
                for tunnel in response.json()["result"]
            ]
        except RequestException as e:
            raise RequestException(f"Failed to get Tunnels data: {e}")
        except JSONDecodeError as e:
            raise JSONDecodeError(
                f"Failed to decode response as JSON: {e.doc}, {e.pos}"
            )

    def get_ingresses(
        self,
    ):
        for tunnel in self.get_tunnels():
            yield from self.get_ingresses_for_tunnel_id(tunnel["id"])

    def get_ingresses_for_tunnel_id(
        self,
        tunnel_id: str,
    ):
        print(f"Getting Ingresses for Tunnel ID: {tunnel_id}")
        try:
            # Make a GET request to the Ingresses URL with the headers
            response = requests.get(
                URL("https://api.cloudflare.com")
                / "client"
                / "v4"
                / "accounts"
                / self.account_id
                / "cfd_tunnel"
                / tunnel_id
                / "configurations",
                headers=self.headers,
            )
            # Raise an exception if the request failed
            response.raise_for_status()
            # Parse the response as JSON and append it to the result
            return [
                {
                    "_expires": response.expires.isoformat(),
                    "tunnel_id": tunnel_id,
                    "sort": ingress.get("id"),
                    "url": (
                        URL(f'https://{ingress["hostname"]}') / ingress.get("path", "")
                    )
                    .with_scheme("https")
                    .human_repr(),
                    "service": ingress["service"],
                    "origin_request": ingress.get("originRequest", {}),
                }
                for ingress in response.json()["result"]["config"]["ingress"]
                if ingress["service"] != "http_status:404"
            ]
        except RequestException as e:
            raise RequestException(f"Failed to get Ingresses data: {e}")
        except JSONDecodeError as e:
            raise JSONDecodeError(
                f"Failed to decode response as JSON: {e.doc}, {e.pos}"
            )
