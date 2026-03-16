# Compose files (Ignition)

All files are Compose spec–compliant and work with **Docker** and **Podman**. The Ignition CLI (Python `ignition.compose`) runs `docker compose` or `podman compose` based on inventory `defaults.runtime` or `DOCKER_OR_PODMAN`.

| File                       | Services              | Ports                            |
| -------------------------- | --------------------- | -------------------------------- |
| `broker-activemq.yml`      | ActiveMQ Classic      | 61616 (OpenWire), 8161 (console) |
| `broker-kafka.yml`         | Zookeeper, Kafka      | 2181, 9092                       |
| `elasticsearch-kibana.yml` | Elasticsearch, Kibana | 9200, 5601                       |
| `keycloak.yml`             | Keycloak (dev mode)   | 8080                             |

**Note:** Elasticsearch and Kibana share one file so they run on the same network. In the inventory, both the `elasticsearch` and `kibana` components point to `compose/elasticsearch-kibana.yml`; starting either one brings up both services.
