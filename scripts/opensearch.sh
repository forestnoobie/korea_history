# Create network and volume if they don't exist
docker network create opensearch-net 2>/dev/null || true
docker volume create opensearch-data 2>/dev/null || true

docker run --rm --name es01 --network opensearch-net \
  -e "OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=hanSHin@1" \
  -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "plugins.security.disabled=true" \
  -v opensearch-data:/usr/share/opensearch/data \
  opensearchproject/opensearch:3.1.0
 
  
docker run -d --rm --name opensearch-dashboards --network opensearch-net \
  -p 8002:5601 \
  -e OPENSEARCH_USERNAME=admin \
  -e OPENSEARCH_PASSWORD=hanSHin@1 \
    -e DISABLE_SECURITY_DASHBOARDS_PLUGIN=true \
  -e OPENSEARCH_SSL_VERIFICATIONMODE=none \
  -e NODE_OPTIONS="--openssl-legacy-provider" \
  -e OPENSEARCH_HOSTS='["http://es01:9200"]' \
  opensearchproject/opensearch-dashboards:3.1.0
  
