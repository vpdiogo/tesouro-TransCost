"""Cliente para a API CKAN do Tesouro Transparente."""

import logging
import time

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://www.tesourotransparente.gov.br/ckan/dataset"

DATASETS = {
    "pessoal_ativo": "custos-por-itens-de-custos-pessoal-ativo",
    "pessoal_inativo": "dados-de-custos-com-pessoal-inativo-do-governo-federal",
    "pensionista": "dados-de-custos-pensionistas-do-governo-federal",
    "demais_custos": "gestao-por-centros-de-custos-demais-custos",
    "depreciacao": "custos-por-itens-de-custos-depreciacao",
    "transferencia": "custos-por-itens-de-custos-transferencia",
}

CKAN_API = "https://www.tesourotransparente.gov.br/ckan/api/3/action"
PAGE_SIZE = 250
MAX_RETRIES = 3
RETRY_BACKOFF = 2


class TesouroClient:
    """Fetches data from the Tesouro Nacional CKAN API."""

    def __init__(self, timeout=30):
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.timeout = timeout

    def _get_resource_url(self, dataset_slug):
        """Get the first JSON resource URL from a CKAN dataset."""
        url = f"{CKAN_API}/package_show"
        resp = self._request(url, params={"id": dataset_slug})
        resources = resp.get("result", {}).get("resources", [])
        for resource in resources:
            if resource.get("format", "").upper() == "JSON":
                return resource["url"]
        if resources:
            return resources[0]["url"]
        raise ValueError(f"No resources found for dataset {dataset_slug}")

    def _request(self, url, params=None):
        """Make a request with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                resp.raise_for_status()
                return resp.json()
            except (requests.RequestException, ValueError) as exc:
                if attempt == MAX_RETRIES - 1:
                    raise
                wait = RETRY_BACKOFF ** (attempt + 1)
                logger.warning("Request failed (attempt %d): %s. Retrying in %ds...", attempt + 1, exc, wait)
                time.sleep(wait)

    def fetch_dataset(self, dataset_key, page=1):
        """Fetch a page of data from a dataset.

        Returns a list of records (dicts).
        """
        slug = DATASETS[dataset_key]
        resource_url = self._get_resource_url(slug)
        separator = "&" if "?" in resource_url else "?"
        paginated_url = f"{resource_url}{separator}pagina={page}"
        data = self._request(paginated_url)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "result" in data:
            return data["result"]
        return data if isinstance(data, list) else []

    def fetch_all_pages(self, dataset_key):
        """Fetch all pages of a dataset.

        Yields records one by one.
        """
        page = 1
        while True:
            logger.info("Fetching %s page %d...", dataset_key, page)
            records = self.fetch_dataset(dataset_key, page=page)
            if not records:
                break
            yield from records
            if len(records) < PAGE_SIZE:
                break
            page += 1
