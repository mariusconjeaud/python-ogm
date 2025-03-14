docker run \
    --name neo4j \
    -p 7687:7687 \
    -d \
    --env NEO4J_AUTH=neo4j/foobarbaz \
    --env NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
    --env NEO4JLABS_PLUGINS='["apoc"]' \
    --rm \
    neo4j:$1
