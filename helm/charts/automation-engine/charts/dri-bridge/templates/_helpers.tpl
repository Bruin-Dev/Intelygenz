{{/*
Expand the name of the chart.
*/}}
{{- define "dri-bridge.name" -}}
{{- default "dri-bridge" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "dri-bridge.fullname" -}}
{{- $name := default "dri-bridge" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "dri-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "dri-bridge.labels" -}}
helm.sh/chart: {{ include "dri-bridge.chart" . }}
{{ include "dri-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: dri-bridge
microservice-type: capability
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "dri-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "dri-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of dri-bridge
*/}}
{{- define "dri-bridge.configmapName" -}}
{{ include "dri-bridge.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of dri-bridge
*/}}
{{- define "dri-bridge.secretName" -}}
{{ include "dri-bridge.fullname" . }}-secret
{{- end }}