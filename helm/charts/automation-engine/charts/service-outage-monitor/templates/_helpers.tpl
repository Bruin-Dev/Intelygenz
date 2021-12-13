{{/*
Expand the name of the chart.
*/}}
{{- define "service-outage-monitor.name" -}}
{{- default "som" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "service-outage-monitor.fullname" -}}
{{- $name := default "som" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "service-outage-monitor.Chart" -}}
{{- printf "%s-%s" $.Chart.Name $.Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "service-outage-monitor.labels" -}}
helm.sh/chart: {{ include "service-outage-monitor.Chart" $ }}
{{ include "service-outage-monitor.selectorLabels" $ }}
{{- if $.Chart.AppVersion }}
app.kubernetes.io/version: {{ $.Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
microservice-type: case-of-use
environment-name: "{{ $.Values.global.environment }}"
current-environment: {{ $.Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "service-outage-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "service-outage-monitor.name" $ }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
