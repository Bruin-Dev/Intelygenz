{{/*
Expand the name of the chart.
*/}}
{{- define "hawkeye-customer-cache.name" -}}
{{- default "hawkeye-customer-cache" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "hawkeye-customer-cache.fullname" -}}
{{- $name := default "hawkeye-customer-cache" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "hawkeye-customer-cache.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "hawkeye-customer-cache.labels" -}}
helm.sh/chart: {{ include "hawkeye-customer-cache.chart" . }}
{{ include "hawkeye-customer-cache.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: hawkeye-customer-cache
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "hawkeye-customer-cache.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hawkeye-customer-cache.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of hawkeye-customer-cache
*/}}
{{- define "hawkeye-customer-cache.configmapName" -}}
{{ include "hawkeye-customer-cache.fullname" . }}-configmap
{{- end }}