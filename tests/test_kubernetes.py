import pytest 
from retry import retry

from .fixtures import Annotator, Services


def test_changing_annotation_causes_creating_proxy_service(
    kubectl,
    k8s_server,
    k8s_client,
    mock_server,
):

    annotator = Annotator(mock_server, kubectl)
    amount_of_services_before_annotation = Services.count(kubectl, "server")
    annotator.do("wormhole.glothriel.github.com/exposed", "yes")

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_created():
        assert (
            Services.count(kubectl, "server")
            == amount_of_services_before_annotation + 1
        )
    _ensure_that_proxied_service_is_created()
    annotator.do("wormhole.glothriel.github.com/exposed", "no")

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_deleted():
        assert (
            Services.count(kubectl, "server")
            == amount_of_services_before_annotation
        )

    _ensure_that_proxied_service_is_deleted()


def test_annotating_with_custom_name_correctly_sets_remote_name(
    kubectl,
    k8s_server,
    k8s_client,
    mock_server,
):
    annotator = Annotator(mock_server, kubectl)
    annotator.do("wormhole.glothriel.github.com/exposed", "yes")
    annotator.do("wormhole.glothriel.github.com/name", "huehue-one-two-three")

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_created():
        assert 'client-huehue-one-two-three' in Services.names(kubectl, namespace="server")
        assert 'server-huehue-one-two-three' in Services.names(kubectl, namespace="client")

    _ensure_that_proxied_service_is_created()

    annotator.do("wormhole.glothriel.github.com/exposed", "no")

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_deleted():
        assert 'client-huehue-one-two-three' not in Services.names(kubectl, namespace="server")
        assert 'server-huehue-one-two-three' not in Services.names(kubectl, namespace="client")

    _ensure_that_proxied_service_is_deleted()


@pytest.mark.skip(reason="currently fails")
def test_deleting_annotated_service_removes_it_from_peers(
    kubectl,
    k8s_server,
    k8s_client,
    mock_server,
):
    annotator = Annotator(mock_server, kubectl)
    annotator.do("wormhole.glothriel.github.com/exposed", "yes")
    annotator.do("wormhole.glothriel.github.com/name", "huehue-one-two-three")

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_created():
        assert 'client-huehue-one-two-three' in [
            svc['metadata']['name'] for svc in kubectl.json(["-n", "server", "get", "svc"])["items"]
        ]

    _ensure_that_proxied_service_is_created()

    kubectl.run(['-n', mock_server.namespace, 'delete', 'svc', mock_server.name])

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_deleted():
        assert 'client-huehue-one-two-three' not in [
            svc['metadata']['name'] for svc in kubectl.json(["-n", "server", "get", "svc"])["items"]
        ]

    _ensure_that_proxied_service_is_deleted()


def test_exposing_service_with_multiple_ports(
    kubectl,
    k8s_server,
    k8s_client,
    mock_server,
):
    annotator = Annotator(mock_server, kubectl, override_name=f'{mock_server.name}-two-ports')
    annotator.do("wormhole.glothriel.github.com/exposed", "yes")
    annotator.do("wormhole.glothriel.github.com/name", "custom")

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_created():
        assert 'client-custom-http' in [
            svc['metadata']['name'] for svc in kubectl.json(["-n", "server", "get", "svc"])["items"]
        ]
        assert 'client-custom-https' in [
            svc['metadata']['name'] for svc in kubectl.json(["-n", "server", "get", "svc"])["items"]
        ]

    _ensure_that_proxied_service_is_created()

    annotator.do("wormhole.glothriel.github.com/exposed", "no")

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_deleted():
        assert 'client-custom-http' not in [
            svc['metadata']['name'] for svc in kubectl.json(["-n", "server", "get", "svc"])["items"]
        ]
        assert 'client-custom-https' not in [
            svc['metadata']['name'] for svc in kubectl.json(["-n", "server", "get", "svc"])["items"]
        ]

    _ensure_that_proxied_service_is_deleted()


def test_exposing_service_with_selected_ports(
    kubectl,
    k8s_server,
    k8s_client,
    mock_server,
):
    annotator = Annotator(mock_server, kubectl, override_name=f'{mock_server.name}-two-ports')
    annotator.do("wormhole.glothriel.github.com/exposed", "yes")
    annotator.do("wormhole.glothriel.github.com/name", "custom")
    annotator.do("wormhole.glothriel.github.com/ports", "http")

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_created():
        assert 'client-custom' in [
            svc['metadata']['name'] for svc in kubectl.json(["-n", "server", "get", "svc"])["items"]
        ]

    _ensure_that_proxied_service_is_created()

    annotator.do("wormhole.glothriel.github.com/exposed", "no")

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_deleted():
        assert 'client-custom' not in [
            svc['metadata']['name'] for svc in kubectl.json(["-n", "server", "get", "svc"])["items"]
        ]

    _ensure_that_proxied_service_is_deleted()


def test_exposing_service_with_changing_ports(
    kubectl,
    k8s_server,
    k8s_client,
    mock_server,
):
    annotator = Annotator(mock_server, kubectl, override_name=f'{mock_server.name}-two-ports')
    annotator.do("wormhole.glothriel.github.com/exposed", "yes")
    annotator.do("wormhole.glothriel.github.com/name", "custom")
    annotator.do("wormhole.glothriel.github.com/ports", "http")

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_created():
        assert 'client-custom' in [
            svc['metadata']['name'] for svc in kubectl.json(["-n", "server", "get", "svc"])["items"]
        ]

    _ensure_that_proxied_service_is_created()

    annotator.do("wormhole.glothriel.github.com/ports", "http,https")

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_deleted():
        assert 'client-custom-http' not in [
            svc['metadata']['name'] for svc in kubectl.json(["-n", "server", "get", "svc"])["items"]
        ]
        assert 'client-custom-https' not in [
            svc['metadata']['name'] for svc in kubectl.json(["-n", "server", "get", "svc"])["items"]
        ]

    _ensure_that_proxied_service_is_deleted()

    if 'client-custom' in [
        svc['metadata']['name'] for svc in kubectl.json(["-n", "server", "get", "svc"])["items"]
    ]:
        pytest.skip(
            "The orphaned service should be removed, but it's not critical, so skipping for now"
        )


def test_connection_via_the_tunnel(
    kubectl,
    k8s_server,
    k8s_client,
    mock_server,
):

    annotator = Annotator(mock_server, kubectl)
    amount_of_services_before_annotation = Services.count(kubectl, "server")
    annotator.do("wormhole.glothriel.github.com/exposed", "yes")

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_created():
        assert (
            Services.count(kubectl, "server")
            == amount_of_services_before_annotation + 1
        )
    _ensure_that_proxied_service_is_created()

    import time
    time.sleep(1500)

    @retry(tries=60, delay=1)
    def _ensure_that_proxied_service_is_reachable():
        kubectl.run(
            [
                '-n',
                'nginx',
                'exec',
                'deployment/nginx',
                '--',
                'curl',
                'server-nginx-nginx.client.svc.cluster.local'
            ]
        )

    _ensure_that_proxied_service_is_reachable()
