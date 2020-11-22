This directory contains example Kubernetes manifests deploying to a `tws`
namespace, and populating secrets containing the account username and password.
Everything is wrapped up in a `Makefile`.

The TWS configuration file is gzipped and stored in a separate secret. Ports
are exposed through a cluster load balancer with DNS names like
`paper.tws.svc.cluster.local` and `live.tws.svc.cluster.local`.
