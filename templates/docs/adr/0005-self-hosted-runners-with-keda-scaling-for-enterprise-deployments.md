# ADR 0005: Self-Hosted Runners with KEDA Scaling for Enterprise Deployments

## Status
Accepted

## Context
Deploying enterprise platform-engineering templates involves managing resources that are completely isolated from the public internet (via Private Endpoints and Network Security Groups, as per ADR 0003 and ADR 0004). Standard, public cloud-hosted runners (such as GitHub-hosted runner pools or default Microsoft-hosted agents in Azure DevOps) cannot deploy to these isolated environments because they lack direct network routes into our private Virtual Networks.

To run deployment pipelines, we need runners located inside our private networks. However, maintaining static self-hosted virtual machines for runners presents challenges:
1. **Under-utilization**: Idle VMs consume resources and incur unnecessary hourly compute costs.
2. **Queued Workflows**: High-intensity developer periods lead to bottlenecked pipelines if the number of static VMs is insufficient.
3. **Security Hygiene**: Runners should ideally be ephemeral, running in clean-slate container environments to prevent state leakage and file system residue from prior jobs.

We need a scalable, secure, and cost-effective runner infrastructure that resides within our private network boundary.

## Decision
For enterprise-tier deployments, we will deploy self-hosted ephemeral runners inside an Azure Kubernetes Service (AKS) cluster and use Kubernetes Event-driven Autoscaling (KEDA) to scale them on demand.

- **Private Placement**: The AKS cluster running our self-hosted runner pool will be deployed within a dedicated subnet inside our private Virtual Network, allowing direct network access to Private Endpoints and private services.
- **Ephemeral Runners**: Runners will run as short-lived Docker containers (e.g., using GitHub Actions Runner Controller (ARC) or Azure DevOps self-hosted Docker agent patterns). Each runner pod will process exactly one job and then automatically terminate.
- **KEDA Autoscaling**: We will configure KEDA with specialized scalers (such as the `github-runner` scaler or `azure-pipelines` scaler). KEDA will query the pipeline system queue length and dynamically spin up runner pods in response to active deployment jobs, scaling down to zero when idle.
- **No Long-Lived Credentials**: Runner pods will utilize Managed Identities (User-Assigned Managed Identity via AKS Workload Identity) to authenticate to Azure resources, avoiding the need for stored secrets on the runner pods.

## Consequences

### Positive
- **Secure Network Access**: Ephemeral runners reside inside our private virtual network, enabling safe deployment to databases, Key Vaults, and networks isolated behind Private Endpoints.
- **Optimal Cost Efficiency**: By scaling down to zero during nights, weekends, or low-activity periods, we eliminate idle VM costs.
- **High Performance and Scalability**: Instantly scales up dozens of parallel runners during high-volume deployment periods, eliminating pipeline queues.
- **Increased Security Hygiene**: Ephemeral runner containers guarantee a clean, uncompromised workspace for every pipeline execution.

### Negative / Neutral
- **Infrastructure Complexity**: Requires managing an AKS cluster, installing Helm charts, and maintaining KEDA custom resource definitions (CRDs).
- **Cluster Bootstrapping**: There is an initial latency of a few seconds for a runner pod to schedule and register with GitHub/Azure DevOps when starting from zero.
- **Network Routing Overhead**: Requires careful IP allocation inside the virtual network, as AKS runner pods can consume many private IP addresses depending on the CNI configuration.

## References
- [ADR 0001: Record Architecture Decisions](0001-record-architecture-decisions.md)
- [ADR 0003: Private Endpoints and Network Isolation for Stateful Resources](0003-private-endpoints-and-network-isolation-for-stateful-resources.md)
- [Kubernetes Event-driven Autoscaling (KEDA)](https://keda.sh/)
- [GitHub Actions Runner Controller (ARC)](https://github.com/actions/actions-runner-controller)
- [Run a Self-Hosted Agent in Docker (Azure DevOps)](https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/docker)
