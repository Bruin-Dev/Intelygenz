{{/*
Expand the name of the chart.
*/}}
{{- define "hawkeye-outage-monitor.name" -}}
{{- default "hawkeye-outage-monitor" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "hawkeye-outage-monitor.fullname" -}}
{{- $name := default "hawkeye-outage-monitor" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "hawkeye-outage-monitor.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "hawkeye-outage-monitor.labels" -}}
helm.sh/chart: {{ include "hawkeye-outage-monitor.chart" . }}
{{ include "hawkeye-outage-monitor.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: hawkeye-outage-monitor
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "hawkeye-outage-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hawkeye-outage-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of hawkeye-outage-monitor
*/}}
{{- define "hawkeye-outage-monitor.configmapName" -}}
{{ include "hawkeye-outage-monitor.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of hawkeye-outage-monitor
*/}}
{{- define "hawkeye-outage-monitor.secretName" -}}
{{ include "hawkeye-outage-monitor.fullname" . }}-secret
{{- end }}