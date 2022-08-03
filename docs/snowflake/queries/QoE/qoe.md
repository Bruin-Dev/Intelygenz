QOE
---
Snowflake query

```SQL
USE DATABASE METTEL_DEVELOP;
USE SCHEMA VELOCLOUD;

SELECT TOP 1 *
FROM LINKS_QOE_METRICS_PLAIN;
```

Results:
* RECORD_METADATA
  * CreateTime: Unix time. Time the record was pull from velocloud. 
  * Offset: Index of the data in Kafka.
  * Partition: kafka partition parent.
  * Topic: kafka queue streaming the data.

Example of RECORD_METADATA:
```json
{
  "CreateTime": 1657092759530,
  "offset": 2430,
  "partition": 1,
  "topic": "velocloud_get_links_qoe_metrics_plain_develop"
}
```

* RECORD_CONTENT

The schema of the data is equal to the body response from the Velocloud API:

Link: [Velocloud API Link](https://developer.vmware.com/apis/1237/velocloud-sdwan-vco-api)

Section: **POST /linkQualityEvent/getLinkQualityEvents**

(see attached file QoE.json for a sample of QoE content)

Sample queries
--------------
Find host and enterprise ID by company name:
````SQL
SELECT * 
FROM V_COMPANY_IDENTIFIERS
WHERE COMPANY LIKE '%FIS%';
````

Discover edges for FIS
````SQL
SELECT RECORD_CONTENT:edge_id
FROM LINKS_QOE_METRICS_PLAIN
WHERE RECORD_CONTENT:host LIKE 'metvco04.mettel.net' AND RECORD_CONTENT:enterprise_id=269
GROUP BY RECORD_CONTENT:edge_id;
````

All edges data for one FIS instance
````SQL
SELECT *
FROM LINKS_QOE_METRICS_PLAIN
WHERE RECORD_CONTENT:host LIKE 'metvco04.mettel.net' AND RECORD_CONTENT:enterprise_id=269;
````

