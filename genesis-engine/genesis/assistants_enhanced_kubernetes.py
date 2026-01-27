"""
Enhanced Kubernetes Advisor Assistant

Comprehensive Kubernetes security and optimization covering:
- CIS Kubernetes Benchmark
- Pod Security Standards (privileged, baseline, restricted)
- Network policies
- Resource management (requests, limits, QoS)
- Health checks (liveness, readiness, startup probes)
- Autoscaling (HPA, VPA, Cluster Autoscaler)
- GitOps patterns (ArgoCD, Flux)
- Cost optimization
- RBAC best practices

References:
- CIS Kubernetes Benchmark: https://www.cisecurity.org/benchmark/kubernetes
- Kubernetes Documentation: https://kubernetes.io/docs/
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class KubernetesFinding(BaseModel):
    """Structured Kubernetes finding output"""

    finding_id: str = Field(..., description="Unique identifier (K8S-001, etc.)")
    title: str = Field(..., description="Brief title of the issue")
    severity: str = Field(..., description="CRITICAL/HIGH/MEDIUM/LOW")
    category: str = Field(..., description="Security/Resources/Networking/Reliability")

    cis_benchmark: str = Field(default="", description="CIS Benchmark reference")
    resource_type: str = Field(default="", description="Pod, Deployment, Service, etc.")
    namespace: str = Field(default="", description="Affected namespace")

    current_config: str = Field(default="", description="Current YAML config")
    secure_config: str = Field(default="", description="Secure YAML config")
    explanation: str = Field(default="", description="Why this matters")

    tools: List[Dict[str, str]] = Field(default_factory=list)
    remediation: Dict[str, str] = Field(default_factory=dict)


class EnhancedKubernetesAssistant:
    """Enhanced Kubernetes Advisor with security and optimization expertise"""

    def __init__(self):
        self.name = "Enhanced Kubernetes Advisor"
        self.version = "2.0.0"
        self.standards = ["CIS Benchmark", "Pod Security Standards", "RBAC"]

    # =========================================================================
    # POD SECURITY STANDARDS
    # =========================================================================

    @staticmethod
    def pod_security_standards() -> Dict[str, Any]:
        """Pod Security Standards (PSS) - replacement for PSP"""
        return {
            "levels": {
                "privileged": "Unrestricted (for system-level workloads only)",
                "baseline": "Minimal restrictions (prevent known privilege escalations)",
                "restricted": "Heavily restricted (current best practices)",
            },
            "bad_config": """
# BAD: Running as root with all capabilities
apiVersion: v1
kind: Pod
metadata:
  name: insecure-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      runAsUser: 0  # Root!
      privileged: true  # Full host access!
      allowPrivilegeEscalation: true
    volumeMounts:
    - name: host-root
      mountPath: /host
  volumes:
  - name: host-root
    hostPath:
      path: /  # Mounting host root filesystem!
            """,
            "secure_config": """
# GOOD: Restricted Pod Security Standard compliant
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:v1.2.3  # Specific version, not latest!
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
          - ALL
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "500m"
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: cache
      mountPath: /var/cache
  volumes:
  - name: tmp
    emptyDir: {}
  - name: cache
    emptyDir: {}
            """,
            "namespace_enforcement": """
# Enforce PSS at namespace level
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
            """,
        }

    # =========================================================================
    # RESOURCE MANAGEMENT
    # =========================================================================

    @staticmethod
    def resource_management() -> Dict[str, Any]:
        """Resource requests, limits, and QoS classes"""
        return {
            "qos_classes": {
                "Guaranteed": "requests == limits for all containers",
                "Burstable": "requests < limits for at least one container",
                "BestEffort": "No requests or limits set (evicted first!)",
            },
            "bad_config": """
# BAD: No resource limits (BestEffort QoS - evicted first)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: no-limits
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest
        # No resources defined - bad!
            """,
            "good_config": """
# GOOD: Proper resource management
apiVersion: apps/v1
kind: Deployment
metadata:
  name: well-configured
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp:v1.2.3
        resources:
          requests:
            memory: "256Mi"   # Scheduler uses this
            cpu: "250m"       # 0.25 CPU cores
          limits:
            memory: "512Mi"   # OOMKilled if exceeded
            cpu: "1000m"      # Throttled if exceeded, not killed
        # Liveness: Is container alive?
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          failureThreshold: 3
        # Readiness: Can container receive traffic?
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        # Startup: For slow-starting containers
        startupProbe:
          httpGet:
            path: /healthz
            port: 8080
          failureThreshold: 30
          periodSeconds: 10
            """,
            "right_sizing": """
# Use VPA recommendations to right-size
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  updatePolicy:
    updateMode: "Off"  # Just recommendations, don't auto-update
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        cpu: 100m
        memory: 50Mi
      maxAllowed:
        cpu: 2
        memory: 2Gi
            """,
        }

    # =========================================================================
    # NETWORK POLICIES
    # =========================================================================

    @staticmethod
    def network_policies() -> Dict[str, Any]:
        """Network policies for pod-to-pod communication"""
        return {
            "default_deny": """
# First: Deny all traffic by default
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}  # Applies to all pods
  policyTypes:
  - Ingress
  - Egress
            """,
            "allow_specific": """
# Then: Allow specific traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-api
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    - namespaceSelector:
        matchLabels:
          name: production
    ports:
    - protocol: TCP
      port: 8080

---
# Allow API to access database
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-db
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: database
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api
    ports:
    - protocol: TCP
      port: 5432

---
# Allow egress to external services
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-egress-external
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 10.0.0.0/8      # Block internal
        - 172.16.0.0/12   # Block internal
        - 192.168.0.0/16  # Block internal
    ports:
    - protocol: TCP
      port: 443
            """,
        }

    # =========================================================================
    # AUTOSCALING
    # =========================================================================

    @staticmethod
    def autoscaling() -> Dict[str, Any]:
        """HPA, VPA, and Cluster Autoscaler configuration"""
        return {
            "hpa": """
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
            """,
            "pod_disruption_budget": """
# Ensure availability during rollouts
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
spec:
  minAvailable: 2  # Or use maxUnavailable: 1
  selector:
    matchLabels:
      app: api
            """,
        }

    # =========================================================================
    # RBAC
    # =========================================================================

    @staticmethod
    def rbac_best_practices() -> Dict[str, Any]:
        """RBAC configuration best practices"""
        return {
            "least_privilege": """
# BAD: Cluster-admin for application
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: app-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin  # Too powerful!
subjects:
- kind: ServiceAccount
  name: app-sa
  namespace: production

---
# GOOD: Minimal permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-role
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  resourceNames: ["app-config", "app-secrets"]  # Specific resources only
  verbs: ["get"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]  # Read-only

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-rolebinding
  namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: app-role
subjects:
- kind: ServiceAccount
  name: app-sa
  namespace: production
            """,
        }

    # =========================================================================
    # SECRETS MANAGEMENT
    # =========================================================================

    @staticmethod
    def secrets_management() -> Dict[str, Any]:
        """Kubernetes secrets management best practices"""
        return {
            "bad": '''
# BAD: Hardcoded secrets in manifests
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    env:
    - name: DATABASE_PASSWORD
      value: "supersecret123"  # Exposed in YAML!
    - name: API_KEY
      value: "sk-abc123"       # Committed to git!
            ''',
            "native_secrets": '''
# BETTER: Kubernetes Secrets (but still base64 encoded, not encrypted!)
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: production
type: Opaque
data:
  # Base64 encoded (not secure by itself!)
  database-password: c3VwZXJzZWNyZXQxMjM=
  api-key: c2stYWJjMTIz

---
# Reference secrets in pods
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    env:
    - name: DATABASE_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: database-password
    # Or mount as files
    volumeMounts:
    - name: secrets
      mountPath: "/etc/secrets"
      readOnly: true
  volumes:
  - name: secrets
    secret:
      secretName: app-secrets
            ''',
            "external_secrets": '''
# GOOD: External Secrets Operator (pulls from Vault, AWS, etc.)
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-store
  namespace: production
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "my-app"

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-store
    kind: SecretStore
  target:
    name: app-secrets
    creationPolicy: Owner
  data:
  - secretKey: database-password
    remoteRef:
      key: production/database
      property: password
  - secretKey: api-key
    remoteRef:
      key: production/api
      property: key
            ''',
            "sealed_secrets": '''
# GOOD: Sealed Secrets (encrypted secrets in Git)
# Install kubeseal CLI and controller

# 1. Create regular secret
kubectl create secret generic app-secrets \\
  --from-literal=password=supersecret \\
  --dry-run=client -o yaml > secret.yaml

# 2. Seal it (encrypted with cluster's public key)
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# 3. Result - safe to commit to Git
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: app-secrets
  namespace: production
spec:
  encryptedData:
    password: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEq...
            ''',
            "sops": '''
# GOOD: SOPS with age/GPG encryption
# secrets.yaml (encrypted with SOPS)
apiVersion: v1
kind: Secret
metadata:
    name: app-secrets
data:
    password: ENC[AES256_GCM,data:abc123==,iv:...]
sops:
    age:
        - recipient: age1ql3z7hjy54pw3hyww5ayf...
    lastmodified: "2024-01-15T10:00:00Z"
    mac: ENC[AES256_GCM,data:xyz789...]
    version: 3.8.1

# Decrypt and apply
sops -d secrets.yaml | kubectl apply -f -

# Or use SOPS with Flux/ArgoCD for GitOps
            ''',
        }

    # =========================================================================
    # GITOPS PATTERNS
    # =========================================================================

    @staticmethod
    def gitops_patterns() -> Dict[str, Any]:
        """GitOps patterns with ArgoCD and Flux"""
        return {
            "argocd_application": '''
# ArgoCD Application
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/my-app
    targetRevision: HEAD
    path: kubernetes/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true      # Remove resources not in Git
      selfHeal: true   # Revert manual changes
    syncOptions:
    - CreateNamespace=true
    - PrunePropagationPolicy=foreground
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
            ''',
            "argocd_app_of_apps": '''
# ArgoCD App of Apps pattern
# Root application that manages other applications
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/gitops
    targetRevision: HEAD
    path: apps  # Contains Application manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true

# apps/my-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/my-app
    path: kubernetes
  destination:
    server: https://kubernetes.default.svc
    namespace: production
            ''',
            "flux_kustomization": '''
# Flux CD Kustomization
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  timeout: 3m
  retryInterval: 1m
  path: ./kubernetes/overlays/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: my-app
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: my-app
      namespace: production
  postBuild:
    substitute:
      ENVIRONMENT: production
      REPLICAS: "3"

---
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/myorg/my-app
  ref:
    branch: main
  secretRef:
    name: github-token
            ''',
            "image_automation": '''
# Flux Image Automation - auto-update images
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  image: myregistry.io/my-app
  interval: 5m
  secretRef:
    name: registry-credentials

---
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImagePolicy
metadata:
  name: my-app
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: my-app
  policy:
    semver:
      range: 1.x.x  # Only patch updates

---
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageUpdateAutomation
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  sourceRef:
    kind: GitRepository
    name: my-app
  git:
    checkout:
      ref:
        branch: main
    commit:
      author:
        name: Flux
        email: flux@example.com
      messageTemplate: 'Update image to {{.NewTag}}'
    push:
      branch: main
  update:
    path: ./kubernetes
    strategy: Setters
            ''',
        }

    # =========================================================================
    # SERVICE MESH
    # =========================================================================

    @staticmethod
    def service_mesh() -> Dict[str, Any]:
        """Service mesh patterns with Istio"""
        return {
            "istio_sidecar": '''
# Enable Istio sidecar injection
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    istio-injection: enabled

---
# VirtualService for traffic routing
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-app
  namespace: production
spec:
  hosts:
  - my-app
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: my-app
        subset: canary
      weight: 100
  - route:
    - destination:
        host: my-app
        subset: stable
      weight: 90
    - destination:
        host: my-app
        subset: canary
      weight: 10

---
# DestinationRule for subsets
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: my-app
  namespace: production
spec:
  host: my-app
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: UPGRADE
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
    loadBalancer:
      simple: LEAST_REQUEST
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
  subsets:
  - name: stable
    labels:
      version: stable
  - name: canary
    labels:
      version: canary
            ''',
            "mtls": '''
# Enable mTLS cluster-wide
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT  # All traffic must be mTLS

---
# Authorization policy
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-auth
  namespace: production
spec:
  selector:
    matchLabels:
      app: api
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/worker"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/internal/*"]
            ''',
            "circuit_breaker": '''
# Circuit breaker with Istio
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: external-service
  namespace: production
spec:
  host: external-api.example.com
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 10
      http:
        http1MaxPendingRequests: 10
        maxRequestsPerConnection: 1
    outlierDetection:
      consecutive5xxErrors: 3          # Trip after 3 5xx errors
      interval: 10s                    # Check every 10 seconds
      baseEjectionTime: 30s            # Eject for 30 seconds
      maxEjectionPercent: 100          # Can eject all instances
      minHealthPercent: 0
            ''',
        }

    # =========================================================================
    # COST OPTIMIZATION
    # =========================================================================

    @staticmethod
    def cost_optimization() -> Dict[str, Any]:
        """Kubernetes cost optimization strategies"""
        return {
            "right_sizing": '''
# Use VPA recommendations for right-sizing
# 1. Deploy VPA in recommendation mode
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Off"  # Just recommendations
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      minAllowed:
        cpu: 50m
        memory: 64Mi
      maxAllowed:
        cpu: 2
        memory: 4Gi

# 2. Check recommendations
kubectl describe vpa my-app-vpa

# Output shows recommended requests:
# Recommendation:
#   Container Recommendations:
#     Container Name: my-app
#     Lower Bound:
#       Cpu:     25m
#       Memory:  128Mi
#     Target:
#       Cpu:     50m
#       Memory:  256Mi
#     Upper Bound:
#       Cpu:     100m
#       Memory:  512Mi
            ''',
            "spot_instances": '''
# Use spot/preemptible instances for non-critical workloads
# GKE example - node pool with spot instances
apiVersion: container.google.com/v1beta1
kind: NodePool
metadata:
  name: spot-pool
spec:
  config:
    preemptible: true  # Spot instances
    labels:
      node-type: spot
    taints:
    - key: node-type
      value: spot
      effect: NoSchedule  # Only schedule tolerating pods

---
# Schedule appropriate workloads on spot
apiVersion: apps/v1
kind: Deployment
metadata:
  name: batch-processor
spec:
  template:
    spec:
      tolerations:
      - key: node-type
        operator: Equal
        value: spot
        effect: NoSchedule
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: node-type
                operator: In
                values: [spot]
      # Handle preemption gracefully
      terminationGracePeriodSeconds: 30
      containers:
      - name: processor
        # Checkpoint work periodically
            ''',
            "namespace_quotas": '''
# Resource quotas per namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: development
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"
    services: "10"
    secrets: "20"
    configmaps: "20"
    persistentvolumeclaims: "10"

---
# LimitRange for default limits
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: development
spec:
  limits:
  - default:
      cpu: 200m
      memory: 256Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    max:
      cpu: "2"
      memory: 2Gi
    min:
      cpu: 50m
      memory: 64Mi
    type: Container
            ''',
            "cluster_autoscaler": '''
# Cluster Autoscaler configuration
# EKS example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
spec:
  template:
    spec:
      containers:
      - name: cluster-autoscaler
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste  # Minimize wasted resources
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/my-cluster
        - --balance-similar-node-groups
        - --scale-down-enabled=true
        - --scale-down-delay-after-add=10m
        - --scale-down-unneeded-time=10m
        - --scale-down-utilization-threshold=0.5  # Scale down if <50% utilized
            ''',
        }

    # =========================================================================
    # OBSERVABILITY
    # =========================================================================

    @staticmethod
    def observability() -> Dict[str, Any]:
        """Kubernetes observability patterns"""
        return {
            "prometheus_servicemonitor": '''
# Prometheus ServiceMonitor for scraping
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
  namespace: monitoring
  labels:
    release: prometheus  # Matches Prometheus selector
spec:
  selector:
    matchLabels:
      app: my-app
  namespaceSelector:
    matchNames:
    - production
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
    scheme: http
    tlsConfig:
      insecureSkipVerify: true

---
# PrometheusRule for alerts
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: my-app-alerts
  namespace: monitoring
spec:
  groups:
  - name: my-app
    rules:
    - alert: HighErrorRate
      expr: |
        sum(rate(http_requests_total{job="my-app",status=~"5.."}[5m])) /
        sum(rate(http_requests_total{job="my-app"}[5m])) > 0.05
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate in my-app"
        description: "Error rate is {{ $value | humanizePercentage }}"

    - alert: HighLatency
      expr: |
        histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="my-app"}[5m])) by (le)) > 1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High latency in my-app"
        description: "P95 latency is {{ $value }}s"

    - alert: PodNotReady
      expr: |
        kube_pod_status_ready{namespace="production",condition="false"} == 1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Pod not ready"
        description: "Pod {{ $labels.pod }} is not ready"
            ''',
            "distributed_tracing": '''
# OpenTelemetry Collector for tracing
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
  namespace: monitoring
data:
  config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
      jaeger:
        protocols:
          grpc:
            endpoint: 0.0.0.0:14250

    processors:
      batch:
        timeout: 10s
        send_batch_size: 1024
      memory_limiter:
        check_interval: 1s
        limit_mib: 1000

    exporters:
      jaeger:
        endpoint: jaeger-collector.monitoring:14250
        tls:
          insecure: true
      prometheus:
        endpoint: 0.0.0.0:8889

    service:
      pipelines:
        traces:
          receivers: [otlp, jaeger]
          processors: [memory_limiter, batch]
          exporters: [jaeger]
        metrics:
          receivers: [otlp]
          processors: [batch]
          exporters: [prometheus]

---
# App instrumentation
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: app
        env:
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "http://otel-collector.monitoring:4317"
        - name: OTEL_SERVICE_NAME
          value: "my-app"
        - name: OTEL_RESOURCE_ATTRIBUTES
          value: "k8s.namespace.name=$(K8S_NAMESPACE),k8s.pod.name=$(K8S_POD_NAME)"
            ''',
            "logging": '''
# Fluent Bit for log collection
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: logging
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush         5
        Log_Level     info
        Daemon        off
        Parsers_File  parsers.conf

    [INPUT]
        Name              tail
        Tag               kube.*
        Path              /var/log/containers/*.log
        Parser            docker
        DB                /var/log/flb_kube.db
        Mem_Buf_Limit     5MB
        Skip_Long_Lines   On
        Refresh_Interval  10

    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_URL            https://kubernetes.default.svc:443
        Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
        Merge_Log           On
        K8S-Logging.Parser  On
        K8S-Logging.Exclude On

    [OUTPUT]
        Name            es
        Match           *
        Host            elasticsearch.logging
        Port            9200
        Index           kubernetes
        Type            _doc
        Logstash_Format On
        Retry_Limit     False
            ''',
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        category: str,
        cis_benchmark: str,
        resource_type: str,
        current_config: str,
        secure_config: str,
        explanation: str,
    ) -> KubernetesFinding:
        """Generate a structured finding"""
        return KubernetesFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            category=category,
            cis_benchmark=cis_benchmark,
            resource_type=resource_type,
            current_config=current_config,
            secure_config=secure_config,
            explanation=explanation,
            tools=self.get_tool_recommendations(),
            remediation={
                "effort": "LOW" if severity == "LOW" else "MEDIUM",
                "priority": severity
            },
        )

    @staticmethod
    def get_tool_recommendations() -> List[Dict[str, str]]:
        """Get recommended tools for Kubernetes security"""
        return [
            {
                "name": "kube-bench",
                "command": "kube-bench run --targets=node,policies,controlplane",
                "description": "CIS Kubernetes Benchmark compliance checker"
            },
            {
                "name": "Polaris",
                "command": "polaris audit --audit-path ./manifests --format=pretty",
                "description": "Best practices validation for Kubernetes"
            },
            {
                "name": "kubesec",
                "command": "kubesec scan deployment.yaml",
                "description": "Security risk analysis for Kubernetes resources"
            },
            {
                "name": "Trivy",
                "command": "trivy k8s --report=summary cluster",
                "description": "Kubernetes cluster vulnerability scanning"
            },
            {
                "name": "kube-hunter",
                "command": "kube-hunter --remote cluster.example.com",
                "description": "Hunt for security weaknesses in Kubernetes"
            },
            {
                "name": "Falco",
                "command": "falco -r /etc/falco/falco_rules.yaml",
                "description": "Runtime security monitoring"
            },
        ]


def create_enhanced_kubernetes_assistant():
    """Factory function to create Enhanced Kubernetes Advisor Assistant"""
    return {
        "name": "Enhanced Kubernetes Advisor",
        "version": "2.0.0",
        "system_prompt": """You are an expert Kubernetes security and optimization advisor with comprehensive
knowledge of container orchestration best practices. Your expertise covers:

SECURITY:
- CIS Kubernetes Benchmark (all sections)
- Pod Security Standards (privileged, baseline, restricted)
- RBAC best practices and least privilege
- Network policies for microsegmentation
- Secrets management (External Secrets, Sealed Secrets, SOPS)
- Service mesh security (Istio mTLS, authorization policies)
- Runtime security with Falco
- Image signing and admission control

RESOURCE MANAGEMENT:
- Resource requests and limits
- QoS classes (Guaranteed, Burstable, BestEffort)
- Vertical Pod Autoscaler (VPA) for right-sizing
- Horizontal Pod Autoscaler (HPA) configuration
- Cluster Autoscaler tuning
- Pod Disruption Budgets

RELIABILITY:
- Health checks (liveness, readiness, startup probes)
- Rolling updates and deployment strategies
- Pod anti-affinity for high availability
- Priority classes and preemption
- Resource quotas and limit ranges

NETWORKING:
- Network policies for zero-trust
- Service mesh patterns with Istio/Linkerd
- Ingress configuration and TLS
- DNS and service discovery

GITOPS:
- ArgoCD application management
- Flux CD Kustomizations
- App of Apps pattern
- Image automation and promotion

COST OPTIMIZATION:
- Right-sizing with VPA recommendations
- Spot/preemptible instance usage
- Namespace quotas
- Cluster autoscaler tuning
- Pod priority and preemption

OBSERVABILITY:
- Prometheus ServiceMonitors and alerts
- Distributed tracing with OpenTelemetry
- Log aggregation with Fluent Bit
- Grafana dashboards

Analyze Kubernetes manifests and configurations for security issues and optimization opportunities.
Provide specific recommendations with CIS Benchmark references.

Format findings with severity levels and remediation steps.""",
        "assistant_class": EnhancedKubernetesAssistant,
        "finding_model": KubernetesFinding,
        "domain": "devops",
        "subdomain": "kubernetes",
        "tags": ["kubernetes", "k8s", "security", "containers", "devops", "gitops"],
        "tools": EnhancedKubernetesAssistant.get_tool_recommendations(),
        "capabilities": [
            "cis_benchmark_compliance",
            "pod_security_review",
            "rbac_analysis",
            "network_policy_design",
            "resource_optimization",
            "gitops_configuration",
            "cost_optimization",
            "observability_setup"
        ],
    }


if __name__ == "__main__":
    assistant = EnhancedKubernetesAssistant()
    print(f"=== {assistant.name} v{assistant.version} ===\n")
    print(f"Standards: {', '.join(assistant.standards)}\n")

    # Demonstrate Pod Security Standards
    print("--- Pod Security Standards ---")
    pss = assistant.pod_security_standards()
    for level, desc in pss["levels"].items():
        print(f"  {level}: {desc}")

    # Show resource management
    print("\n--- Resource Management ---")
    rm = assistant.resource_management()
    for qos, desc in rm["qos_classes"].items():
        print(f"  {qos}: {desc}")

    # Show network policies
    print("\n--- Network Policies ---")
    np = assistant.network_policies()
    print("  Default deny all: Start with deny, then allow specific")
    print("  Allow specific: Define ingress/egress rules per service")

    # Show autoscaling
    print("\n--- Autoscaling ---")
    autoscale = assistant.autoscaling()
    print("  HPA: Scale based on CPU/memory/custom metrics")
    print("  PDB: Ensure availability during rollouts")

    # Show RBAC best practices
    print("\n--- RBAC Best Practices ---")
    rbac = assistant.rbac_best_practices()
    print("  Least privilege: Role, not ClusterRole when possible")
    print("  Specific resources: resourceNames for targeted access")

    # Show secrets management
    print("\n--- Secrets Management ---")
    secrets = assistant.secrets_management()
    print("  Native Secrets: Base64 encoded, not truly encrypted")
    print("  External Secrets: Pull from Vault, AWS, etc.")
    print("  Sealed Secrets: Encrypted, safe for Git")

    # Show GitOps patterns
    print("\n--- GitOps Patterns ---")
    gitops = assistant.gitops_patterns()
    print("  ArgoCD: Application CRDs with sync policies")
    print("  Flux: Kustomizations with health checks")
    print("  Image automation: Auto-update on new images")

    # Show service mesh
    print("\n--- Service Mesh ---")
    mesh = assistant.service_mesh()
    print("  Istio: Traffic routing, mTLS, authorization")
    print("  Circuit breaker: Outlier detection")

    # Show cost optimization
    print("\n--- Cost Optimization ---")
    cost = assistant.cost_optimization()
    print("  Right-sizing: Use VPA recommendations")
    print("  Spot instances: For non-critical workloads")
    print("  Resource quotas: Limit spending per namespace")

    # Show observability
    print("\n--- Observability ---")
    obs = assistant.observability()
    print("  Prometheus: ServiceMonitors and PrometheusRules")
    print("  Tracing: OpenTelemetry Collector")
    print("  Logging: Fluent Bit to Elasticsearch")

    # Generate sample finding
    print("\n--- Sample Finding ---")
    finding = assistant.generate_finding(
        finding_id="K8S-001",
        title="Container Running as Root",
        severity="HIGH",
        category="Security",
        cis_benchmark="5.2.6",
        resource_type="Deployment",
        current_config="securityContext: {} # No runAsNonRoot",
        secure_config="securityContext:\n  runAsNonRoot: true\n  runAsUser: 1000",
        explanation="Containers should run as non-root to limit potential damage"
    )
    print(f"ID: {finding.finding_id}")
    print(f"Title: {finding.title}")
    print(f"Severity: {finding.severity}")
    print(f"CIS Benchmark: {finding.cis_benchmark}")
    print(f"Resource Type: {finding.resource_type}")
    print(f"Remediation: {finding.remediation}")

    # Show tool recommendations
    print("\n--- Tool Recommendations ---")
    tools = assistant.get_tool_recommendations()
    for tool in tools[:4]:
        print(f"\n{tool['name']}:")
        print(f"  Command: {tool['command']}")
        print(f"  Description: {tool['description']}")

    # Show factory function output
    print("\n--- Factory Function ---")
    config = create_enhanced_kubernetes_assistant()
    print(f"Name: {config['name']}")
    print(f"Version: {config['version']}")
    print(f"Domain: {config['domain']}")
    print(f"Tags: {', '.join(config['tags'])}")
    print(f"Capabilities: {', '.join(config['capabilities'][:3])}...")
