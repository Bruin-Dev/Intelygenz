{{/*
Expand the name of the chart.
*/}}
{{- define "repair-tickets-kre-bridge.name" -}}
{{- default "repair-tickets-kre-bridge" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "repair-tickets-kre-bridge.fullname" -}}
{{- $name := default "repair-tickets-kre-bridge" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "repair-tickets-kre-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "repair-tickets-kre-bridge.labels" -}}
helm.sh/chart: {{ include "repair-tickets-kre-bridge.chart" . }}
{{ include "repair-tickets-kre-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: repair-tickets-kre-bridge
microservice-type: capability
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "repair-tickets-kre-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "repair-tickets-kre-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of repair-tickets-kre-bridge
*/}}
{{- define "repair-tickets-kre-bridge.configmapName" -}}
{{ include "repair-tickets-kre-bridge.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of repair-tickets-kre-bridge
*/}}
{{- define "repair-tickets-kre-bridge.secretName" -}}
{{ include "repair-tickets-kre-bridge.fullname" . }}-secret
{{- end }}