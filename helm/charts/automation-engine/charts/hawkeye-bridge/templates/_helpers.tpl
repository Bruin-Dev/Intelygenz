{{/*
Expand the name of the chart.
*/}}
{{- define "hawkeye-bridge.name" -}}
{{- default "hawkeye-bridge" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "hawkeye-bridge.fullname" -}}
{{- $name := default "hawkeye-bridge" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "hawkeye-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "hawkeye-bridge.labels" -}}
helm.sh/chart: {{ include "hawkeye-bridge.chart" . }}
{{ include "hawkeye-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: cts-bridge
microservice-type: capability
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "hawkeye-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hawkeye-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of hawkeye-bridge
*/}}
{{- define "hawkeye-bridge.configmapName" -}}
{{ include "hawkeye-bridge.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of hawkeye-bridge
*/}}
{{- define "hawkeye-bridge.secretName" -}}
{{ include "hawkeye-bridge.fullname" . }}-secret
{{- end }}