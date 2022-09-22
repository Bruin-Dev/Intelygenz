{{/*
Expand the name of the chart.
*/}}
{{- define "forticloud-poller.name" -}}
{{- default "forticloud-poller" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "forticloud-poller.fullname" -}}
{{- $name := default "forticloud-poller" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "forticloud-poller.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "forticloud-poller.labels" -}}
helm.sh/chart: {{ include "forticloud-poller.chart" . }}
{{ include "forticloud-poller.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: forticloud-poller
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "forticloud-poller.selectorLabels" -}}
app.kubernetes.io/name: {{ include "forticloud-poller.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of forticloud-poller
*/}}
{{- define "forticloud-poller.configmapName" -}}
{{ include "forticloud-poller.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of forticloud-poller
*/}}
{{- define "forticloud-poller.secretName" -}}
{{ include "forticloud-poller.fullname" . }}-secret
{{- end }}
