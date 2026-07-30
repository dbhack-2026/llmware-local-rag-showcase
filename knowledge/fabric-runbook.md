# Fabric deployment runbook

The LLMWare Python service runs as an internal OpenShift deployment. The application image contains Python, LLMWare and the inference runtime. Model weights should normally be mounted read-only from a persistent volume rather than baked into every image.

For CPU inference, start with one replica and a small quantized GGUF model. Each replica loads its own copy of the model into memory, so horizontal scaling multiplies RAM usage.

Spring Boot services call the internal `/v1/ask` endpoint. OAuth authentication, AD-group authorization and audit logging should be handled at the Spring Boot gateway or service-mesh boundary.
