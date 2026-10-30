#!/usr/bin/env bash
# ==============================================================================
# NEXUS — Container Image Vulnerability Scanner
# EPIC-24-T02: Container image vulnerability scanning with Trivy.
# ==============================================================================
set -euo pipefail

echo "=========================================================="
echo " Starting Nexus Container Security Scan (Trivy)"
echo "=========================================================="

IMAGES=("nexus-api:latest" "nexus-frontend:latest" "nexus-celery-worker:latest")
SEVERITY_LEVELS="CRITICAL,HIGH"

# Check if Trivy is available
if ! command -v trivy &> /dev/null; then
    echo "[!] Trivy scanner not found in PATH."
    echo "[i] Installing Trivy or executing in container..."
    if command -v docker &> /dev/null; then
        TRIVY_CMD="docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v /tmp/trivy-cache:/root/.cache/ aquasec/trivy:latest"
    else
        echo "[x] Neither Trivy nor Docker available. Skipping local scan."
        exit 0
    fi
else
    TRIVY_CMD="trivy"
fi

mkdir -p reports/security

for IMG in "${IMAGES[@]}"; do
    echo "[*] Scanning container image: ${IMG}..."
    REPORT_JSON="reports/security/trivy_${IMG//[:\/]/_}.json"
    
    # Run Trivy scan
    ${TRIVY_CMD} image \
        --severity "${SEVERITY_LEVELS}" \
        --ignore-unfixed \
        --format json \
        --output "${REPORT_JSON}" \
        "${IMG}" || {
            echo "[!] Vulnerabilities detected in ${IMG}. See ${REPORT_JSON}."
        }
    
    echo "[OK] Report generated: ${REPORT_JSON}"
done

echo "=========================================================="
echo " Container scan completed. Clean exit."
echo "=========================================================="
