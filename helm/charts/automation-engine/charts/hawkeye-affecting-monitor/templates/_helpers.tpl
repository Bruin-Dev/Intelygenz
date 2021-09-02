{{/*
Expand the name of the chart.
*/}}
{{- define "hawkeye-affecting-monitor.name" -}}
{{- default "hawkeye-affecting-monitor" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "hawkeye-affecting-monitor.fullname" -}}
{{- $name := default "hawkeye-affecting-monitor" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "hawkeye-affecting-monitor.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "hawkeye-affecting-monitor.labels" -}}
helm.sh/chart: {{ include "hawkeye-affecting-monitor.chart" . }}
{{ include "hawkeye-affecting-monitor.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: hawkeye-affecting-monitor
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "hawkeye-affecting-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hawkeye-affecting-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of hawkeye-affecting-monitor
*/}}
{{- define "hawkeye-affecting-monitor.configmapName" -}}
{{ include "hawkeye-affecting-monitor.fullname" . }}-configmap
{{- end }}