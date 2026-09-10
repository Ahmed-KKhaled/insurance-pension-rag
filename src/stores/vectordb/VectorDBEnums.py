from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "QDRANT"
    CHROMA = "CHROMA"
    PGVECTOR = "PGVECTOR"


class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"
    IP = "ip"

class PgVectorTableSchemeEnums(Enum):
    ID = "id"
    TEXT = "text"
    VECTOR = "vector"
    CHUNK_ID = "chunk_id"
    METADATA = "metadata"
    _PREFIX = "pgvector"

class PgVectorDistanceMetodEnums(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"

class PgVectorIndexTypeEnums(Enum):
    HNSW = "hnsw"
    IVFFLAT = "ivfflat"