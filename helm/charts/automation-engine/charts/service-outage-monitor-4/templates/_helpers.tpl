{{/*
Expand the name of the chart.
*/}}
{{- define "service-outage-monitor-4.name" -}}
{{- default "service-outage-monitor-4" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "service-outage-monitor-4.fullname" -}}
{{- $name := default "service-outage-monitor-4" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "service-outage-monitor-4.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "service-outage-monitor-4.labels" -}}
helm.sh/chart: {{ include "service-outage-monitor-4.chart" . }}
{{ include "service-outage-monitor-4.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: service-outage-monitor-4
microservice-type: case-of-use
environment-name: {{ .Values.global.environment }}
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "service-outage-monitor-4.selectorLabels" -}}
app.kubernetes.io/name: {{ include "service-outage-monitor-4.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of service-outage-monitor-4
*/}}
{{- define "service-outage-monitor-4.configmapName" -}}
{{ include "service-outage-monitor-4.fullname" . }}-configmap
{{- end }}