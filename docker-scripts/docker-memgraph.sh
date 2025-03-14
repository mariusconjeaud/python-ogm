docker run \
    --name memgraph \
    -p 7689:7687 \
    -d \
    --env MEMGRAPH_AUTH_ENABLED=true \
    --env MEMGRAPH_USERNAME=neo4j \
    --env MEMGRAPH_PASSWORD=foobarbaz \
    --rm \
    memgraph/memgraph:$1
