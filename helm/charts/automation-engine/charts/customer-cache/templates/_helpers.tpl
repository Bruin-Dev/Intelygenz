{{/*
Expand the name of the chart.
*/}}
{{- define "customer-cache.name" -}}
{{- default "customer-cache" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "customer-cache.fullname" -}}
{{- $name := default "customer-cache" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "customer-cache.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "customer-cache.labels" -}}
helm.sh/chart: {{ include "customer-cache.chart" . }}
{{ include "customer-cache.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: customer-cache
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "customer-cache.selectorLabels" -}}
app.kubernetes.io/name: {{ include "customer-cache.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of customer-cache
*/}}
{{- define "customer-cache.configmapName" -}}
{{ include "customer-cache.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of customer-cache
*/}}
{{- define "customer-cache.secretName" -}}
{{ include "customer-cache.fullname" . }}-secret
{{- end }}