{{/*
Expand the name of the chart.
*/}}
{{- define "intermapper-outage-monitor.name" -}}
{{- default "intermapper-outage-monitor" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "intermapper-outage-monitor.fullname" -}}
{{- $name := default "intermapper-outage-monitor" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "intermapper-outage-monitor.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "intermapper-outage-monitor.labels" -}}
helm.sh/chart: {{ include "intermapper-outage-monitor.chart" . }}
{{ include "intermapper-outage-monitor.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: intermapper-outage-monitor
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "intermapper-outage-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "intermapper-outage-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of intermapper-outage-monitor
*/}}
{{- define "intermapper-outage-monitor.configmapName" -}}
{{ include "intermapper-outage-monitor.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of intermapper-outage-monitor
*/}}
{{- define "intermapper-outage-monitor.secretName" -}}
{{ include "intermapper-outage-monitor.fullname" . }}-secret
{{- end }}