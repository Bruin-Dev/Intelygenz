import base64

from application.repositories.template_management import TemplateRenderer
from config import testconfig


class TestTemplateRenderer:

    def instantiation_test(self):
        config = testconfig
        test_repo = TemplateRenderer(config)
        assert test_repo._config == config

    def ticket_object_to_email_obj_test(self):
        config = testconfig
        template_renderer = TemplateRenderer(config)

        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE1",
                            "displayName": "Test1",
                            "state": "DISCONNECTED",
                        }
                    },
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE2",
                            "displayName": "Test2",
                            "state": "DISCONNECTED",
                        }
                    }
                ]
            }
        }
        test_dict = {'test_key': 'test_value'}

        email = template_renderer.compose_email_object(edges_to_report, 'Latency', test_dict)

        assert 'Service affecting trouble detected: ' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_object_html_elements_test(self):
        base = "src/templates/images/{}"
        kwargs = dict(logo="logo.png",
                      header="header.jpg")
        config = testconfig
        template_renderer = TemplateRenderer(config)
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE1",
                            "displayName": "Test1",
                            "state": "DISCONNECTED",
                        }
                    },
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE2",
                            "displayName": "Test2",
                            "state": "DISCONNECTED",
                        }
                    }
                ]
            }
        }
        test_dict = {'test_key': 'test_value'}

        email = template_renderer.compose_email_object(edges_to_report, 'LATENCY', test_dict)

        assert email["email_data"]["images"][0]["data"] == base64.b64encode(open(base.format(kwargs["logo"]), 'rb')
                                                                            .read()).decode('utf-8')
        assert email["email_data"]["images"][1]["data"] == base64.b64encode(open(base.format(kwargs["header"]), 'rb')
                                                                            .read()).decode('utf-8')

    def compose_email_test(self):
        config = testconfig

        template_renderer = TemplateRenderer(config)

        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE1",
                            "displayName": "Test1",
                            "state": "DISCONNECTED",
                        }
                    },
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE2",
                            "displayName": "Test2",
                            "state": "DISCONNECTED",
                        }
                    }
                ]
            }
        }
        test_dict = {'test_key': 'test_value'}

        email = template_renderer.compose_email_object(edges_to_report, 'LATENCY', test_dict)

        assert 'Service affecting trouble detected: ' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_bandwidth_report_email_test(self):
        config = testconfig

        template_renderer = TemplateRenderer(config)

        report = {
            'name': 'Report - Bandwidth Utilization', 'type': 'bandwidth_utilization',
            'crontab': '20 16 * * *',
            'threshold': 3, 'client_id': 83109, 'trailing_days': 14, 'recipient': 'mettel@intelygenz.com'
        }
        report_items = [{
            'customer': {'client_id': 83109, 'client_name': 'RSI'},
            'location': {
                'address': '621 Hill Ave', 'city': 'Nashville', 'state': 'TN', 'zip': '37210-4714',
                'country': 'USA'
            }, 'serial_number': 'VC05200085762', 'number_of_tickets': 4,
            'bruin_tickets_id': [5081250, 5075176, 5074441, 5073652], 'interfaces': ['GE1']
        }]
        email_obj = {
            'request_id': 'CV6J8M2b6cpMtrMNij43Hc',
            'email_data': {
                'subject': 'Service affecting bandwidth utilization for 14 days',
                'recipient': 'mettel@intelygenz.com', 'text': 'this is the accessible text for the email',
                'html': '<!DOCTYPE html>\n<html\n  xmlns="http://www.w3.org/1999/xhtml"\n  '
                        'xmlns:v="urn:schemas-microsoft-com:vml"\n  '
                        'xmlns:o="urn:schemas-microsoft-com:office:office"\n>\n  <head>\n    <title>Automated Report '
                        'Email Template</title>\n    <!--[if !mso]><!-- -->\n    <meta http-equiv="X-UA-Compatible" '
                        'content="IE=edge" />\n    <!--<![endif]-->\n    <meta http-equiv="Content-Type" '
                        'content="text/html; charset=UTF-8" />\n    <meta name="viewport" '
                        'content="width=device-width, initial-scale=1.0" />\n\n    <style type="text/css">\n@media '
                        'screen {\n    /* latin */\n     @font-face {\n     font-family: \'Raleway\';\n     '
                        'font-style: normal;\n     font-weight: 700;\n     src: local(\'Raleway Bold\'), '
                        'local(\'Raleway-Bold\'), '
                        'url(https://fonts.gstatic.com/s/raleway/v13/1Ptrg8zYS_SKggPNwJYtWqZPANqczVs.woff2) format('
                        '\'woff2\');\n     unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, '
                        'U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, '
                        'U+FFFD;\n     }\n\n     @font-face {\n     font-family: \'Roboto\';\n     font-style: '
                        'normal;\n     font-weight: 400;\n     src: local(\'Roboto\'), local(\'Roboto-Regular\'), '
                        'url(https://fonts.gstatic.com/s/roboto/v19/KFOmCnqEu92Fr1Mu4mxKKTU1Kg.woff2) format('
                        '\'woff2\');\n     unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, '
                        'U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, '
                        'U+FFFD;\n     }\n\n     @font-face {\n     font-family: \'Roboto\';\n     font-style: '
                        'normal;\n     font-weight: 700;\n     src: local(\'Roboto Bold\'), local(\'Roboto-Bold\'), '
                        'url(https://fonts.gstatic.com/s/roboto/v19/KFOlCnqEu92Fr1MmWUlfBBc4AMP6lQ.woff2) format('
                        '\'woff2\');\n     unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, '
                        'U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, '
                        'U+FFFD;\n     }\n}\n      #outlook a {\n        padding: 0;\n      }\n      .ReadMsgBody {\n '
                        '       width: 100%;\n      }\n      .ExternalClass {\n        width: 100%;\n      }\n      '
                        '.ExternalClass * {\n        line-height: 100%;\n      }\n      body {\n        margin: 0;\n  '
                        '      padding: 0;\n        -webkit-text-size-adjust: 100%;\n        -ms-text-size-adjust: '
                        '100%;\n        font-family:\'Roboto\', Arial, Helvetica, sans-serif;\n        '
                        'font-weight:400;\n\n      }\n      table,\n      td {\n        border-collapse: collapse;\n  '
                        '      mso-table-lspace: 0pt;\n        mso-table-rspace: 0pt;\n      }\n\tth {'
                        '\n\t\tbackground-color: #263640;\n\t\tcolor: #ffffff;\n\t\tfont-weight: '
                        'bold;\n\t\tfont-size: 16px;\n\t\tline-height: 22px;\n\t\tpadding: 15px;\n\t\tletter-spacing: '
                        '0.05em;\n\t\tborder: 1px solid #DDDDDD;\n\t}\n      img {\n        border: 0;\n        '
                        'height: auto;\n        line-height: 100%;\n        outline: none;\n        text-decoration: '
                        'none;\n        -ms-interpolation-mode: bicubic;\n      }\n\th2 {'
                        '\n\t\tcolor:#47B585;\n\t\tfont-family:\'Roboto\', Helvetica, Arial, '
                        'sans-serif;\n\t\tletter-spacing:0.25em;\n\t\tfont-size: 18px;\n\t\tline-height: 25px;\n\t}\n '
                        '     p {\n        display: block;\n        color:#596872;\n\t\tfont-size: '
                        '14px;\n\t\tline-height: 20px;\n\t\tfont-family:\'Roboto\', Helvetica, Arial, '
                        'sans-serif;\n\t\tletter-spacing: 0.05em\n      }\n\n      .hide_on_mobile { display: none '
                        '!important;}\n    </style>\n    <!--[if !mso]><!-->\n    <style type="text/css">\n      '
                        '@media only screen and (max-width: 480px) {\n        @-ms-viewport {\n          width: '
                        '320px;\n        }\n        @viewport {\n          width: 320px;\n        }\n      }\n    '
                        '</style>\n    <!--<![endif]-->\n    <!--[if mso]><xml>\n        <o:OfficeDocumentSettings>\n '
                        '         <o:AllowPNG /> <o:PixelsPerInch>96</o:PixelsPerInch>\n        '
                        '</o:OfficeDocumentSettings></xml\n      ><![endif]-->\n    <!--[if lte mso 11]>\n     <style '
                        'type="text/css">\n        .outlook-group-fix {\n          width: 100% !important;\n        '
                        '}\n      </style>\n     <![endif]-->\n <!--[if mso]>\n<style '
                        'type=”text/css”>\n.fallback-font {\nfont-family: Arial, sans-serif;\n}\n</style>\n<!['
                        'endif]-->\n    <style type="text/css">\n      @media only screen and (min-width: 480px) {\n  '
                        '      .mj-column-per-100 {\n          width: 100% !important;\n        }\n        '
                        '.mj-column-per-50 {\n          width: 50% !important;\n        }\n        .mj-column-per-40 '
                        '{\n          width: 40% !important;\n        }\n        .mj-column-per-60 {\n          '
                        'width: 60% !important;\n        }\n        .hide_on_mobile { display: block !important;}\n\n '
                        '       .aligned-left {\n        \ttext-align: left !important;\n        }\n\n          '
                        '.floatLeft {\n          \tfloat: left!important;\n          }\n      }\n    </style>\n  '
                        '</head>\n  <body style="background: #FFFFFF;">\n    <div class="mj-container" '
                        'style="background-color:#FFFFFF;">\n      <!--[if mso | IE]>      <table role="presentation" '
                        'border="0" cellpadding="0" cellspacing="0" width="600" align="center" style="width:600px;">  '
                        '      <tr>          <td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"> '
                        '     <![endif]-->\n      <div style="margin:0px auto;max-width:600px;">\n        <table\n    '
                        '      role="presentation"\n          cellpadding="0"\n          cellspacing="0"\n          '
                        'style="font-size:0px;width:100%;"\n          align="center"\n          border="0"\n        '
                        '>\n          <tbody>\n            <tr>\n              <td\n                '
                        'style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:22px 0px '
                        '22px 0px;"\n              >\n                <!--[if mso | IE]>      <table '
                        'role="presentation" border="0" cellpadding="0" cellspacing="0">        <tr>          <td '
                        'style="vertical-align:top;width:600px;">      <![endif]-->\n                <div\n           '
                        '       class="mj-column-per-100 outlook-group-fix"\n                  '
                        'style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left'
                        ';width:100%;"\n                >\n                  <table\n                    '
                        'role="presentation"\n                    cellpadding="0"\n                    '
                        'cellspacing="0"\n                    style="vertical-align:top;"\n                    '
                        'width="100%"\n                    border="0"\n                  >\n                    '
                        '<tbody>\n                      <tr>\n                        <td\n                          '
                        'style="word-wrap:break-word;font-size:0px;padding:0px 0px 0px 0px;"\n                        '
                        '  align="center"\n                        >\n                          <table\n              '
                        '              role="presentation"\n                            cellpadding="0"\n             '
                        '               cellspacing="0"\n                            '
                        'style="border-collapse:collapse;border-spacing:0px;"\n                            '
                        'align="center"\n                            border="0"\n                          >\n        '
                        '                    <tbody>\n                              <tr>\n                            '
                        '    <td style="width:100px;">\n                                   <a '
                        'href="https://intelygenz.com/terminus-7-ai/">\n                                        '
                        '<img\n                                        alt\n                                        '
                        'height="auto"\n                                        src="cid:logo"\n                      '
                        '                  style="border:none;border-radius:0px;display:block;font-size:13px;outline'
                        ':none;text-decoration:none;width:100px;height:auto;"\n                                       '
                        ' width="100"\n                                   />\n                                   '
                        '</a>\n                                </td>\n                              </tr>\n           '
                        '                 </tbody>\n                          </table>\n                        '
                        '</td>\n                      </tr>\n                    </tbody>\n                  '
                        '</table>\n                </div>\n                <!--[if mso | IE]>      </td></tr></table> '
                        '     <![endif]-->\n              </td>\n            </tr>\n          </tbody>\n        '
                        '</table>\n      </div>\n      <!--[if mso | IE]></td></tr></table><![endif]-->\n\n\t<!-- '
                        'START HEADER -->\n      <!--[if mso | IE]><table role="presentation" border="0" '
                        'cellpadding="0" cellspacing="0" width="600" align="center" style="width:600px;"><tr><td '
                        'style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->\n      <div '
                        'style="margin:0px auto;max-width:600px;">\n        <table role="presentation" '
                        'cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;" align="center" '
                        'border="0">\n          <tbody>\n            <tr>\n              <td '
                        'style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:0px 0px 0px '
                        '0px;">\n                <!--[if mso | IE]><table role="presentation" border="0" '
                        'cellpadding="0" cellspacing="0"><tr><td style="vertical-align:top;width:600px;"><!['
                        'endif]-->\n                <div class="mj-column-per-100 outlook-group-fix" '
                        'style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left'
                        ';width:100%;">\n                  <table role="presentation" cellpadding="0" cellspacing="0" '
                        'style="vertical-align:top;" width="100%" border="0">\n                    <tbody>\n          '
                        '            <tr>\n                        <td '
                        'style="word-wrap:break-word;font-size:0px;padding:0px 0px 0px 0px;" align="center">\n        '
                        '                  <img editable="true" alt="Automation Reports Powered by Intelygenz" '
                        'height="auto" src="cid:header" '
                        'style="border:none;border-radius:0px;display:block;font-size:13px;outline:none;text'
                        '-decoration:none;width:100%;height:auto;" width="600" />\n                        </td>\n    '
                        '                  </tr>\n                    </tbody>\n                  </table>\n          '
                        '      </div>\n                <!--[if mso | IE]></td></tr></table><![endif]-->\n             '
                        ' </td>\n            </tr>\n          </tbody>\n        </table>\n      </div>\n      <!--[if '
                        'mso | IE]></td></tr></table><![endif]-->\n\t<!-- END HEADER -->\n\n\n\n   \t<!-- START INTRO '
                        'TEXT -->\n      <!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" '
                        'cellspacing="0" width="600" align="center" style="width:600px;"><tr><td '
                        'style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->\n      <div '
                        'style="margin:0px auto;max-width:600px;background:#ffffff;">\n        <table '
                        'role="presentation" cellpadding="0" cellspacing="0" style="font-size: 0px; width:100%; '
                        'background: #ffffff;" align="center" border="0">\n          <tbody>\n            <tr>\n      '
                        '        <td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding'
                        ':20px 0px 20px 0px;">\n                <!--[if mso | IE]><table role="presentation" '
                        'border="0" cellpadding="0" cellspacing="0"><tr><td '
                        'style="vertical-align:top;width:600px;"><![endif]-->\n                <div '
                        'class="mj-column-per-100 outlook-group-fix" '
                        'style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left'
                        ';width:100%;">\n                  <table role="presentation" cellpadding="0" cellspacing="0" '
                        'style="vertical-align:top;" width="100%" border="0">\n                    <tbody>\n          '
                        '            <tr>\n                        <td style="word-wrap: break-word; font-size: 0px; '
                        'padding: 0px 20px 0px 20px;" align="center">\n                          <div '
                        'style="cursor:auto;color:#FFFFFF;font-family:\'Roboto\', Helvetica, Arial, sans-serif; '
                        'font-size: 14px; line-height: 20px; text-align:center;">\n                          \t<h2 '
                        'style="color:#47B585;letter-spacing:0.25em; font-size: 18px; line-height: 25px;">Service '
                        'Affecting trouble: Report - Bandwidth Utilization</h2>\n\t\t\t\t\t\t\t<p class="intro" '
                        'style="color:#596872; font-size: 16px; line-height: 22px; font-family:\'Roboto\', Helvetica, '
                        'Arial, sans-serif; letter-spacing: 0.05em;"> in edges (1) VC05200085762</p>\n                '
                        '          </div>\n                        </td>\n                      </tr>\n               '
                        '     </tbody>\n                  </table>\n                </div>\n                <!--[if '
                        'mso | IE]></td></tr></table><![endif]-->\n              </td>\n            </tr>\n          '
                        '</tbody>\n        </table>\n      </div>\n      <!--[if mso | IE]></td></tr></table><!['
                        'endif]-->\n\t<!-- END INTRO TEXT -->\n\n\n\t<!-- START DIVIDER -->\n\t  <!--[if mso | '
                        'IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0" width="600" '
                        'align="center" style="width:600px;"><tr><td '
                        'style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->\n      <div '
                        'style="margin:0px auto;max-width:600px;">\n        <table role="presentation" '
                        'cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;" align="center" '
                        'border="0">\n          <tbody>\n            <tr>\n              <td '
                        'style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding: 0px 20px '
                        '0px 20px;">\n                <!--[if mso | IE]><table role="presentation" border="0" '
                        'cellpadding="0" cellspacing="0"><tr><td style="vertical-align:top;width:600px;"><!['
                        'endif]-->\n                <div class="mj-column-per-100 outlook-group-fix" '
                        'style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left'
                        ';width:100%;">\n                  <table role="presentation" cellpadding="0" cellspacing="0" '
                        'style="vertical-align:top;" width="100%" border="0">\n                    <tbody>\n          '
                        '            <tr>\n                        <td style="word-wrap: break-word; font-size: 0px; '
                        'padding: 10px 25px; padding-top: 10px; padding-bottom: 10px; padding-right: 0px; '
                        'padding-left: 0px;">\n                          <p style="font-size:1px;margin:0px '
                        'auto;border-top:1px solid #DEE1E3;width:100%;"></p>\n                          <!--[if mso | '
                        'IE]><table role="presentation" align="center" border="0" cellpadding="0" cellspacing="0" '
                        'style="font-size:1px;margin:0px auto;border-top:1px solid #DEE1E3;width:100%;" '
                        'width="600"><tr><td style="height:0;line-height:0;"> </td></tr></table><![endif]-->\n        '
                        '                </td>\n                      </tr>\n                    </tbody>\n           '
                        '       </table>\n                </div>\n                <!--[if mso | '
                        'IE]></td></tr></table><![endif]-->\n              </td>\n            </tr>\n          '
                        '</tbody>\n        </table>\n      </div>\n      <!--[if mso | IE]></td></tr></table><!['
                        'endif]-->\n\t<!-- END DIVIDER -->\n\n    \n    \n\t<!-- START DATA TABLE -->\n      <!--[if '
                        'mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0" width="600" '
                        'align="center" style="width:600px;"><tr><td '
                        'style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->\n      <div '
                        'style="margin:0px auto;max-width:600px;background:#ffffff;">\n        <table '
                        'role="presentation" cellpadding="0" cellspacing="0" '
                        'style="font-size:0px;width:100%;background:#ffffff;" align="center" border="0">\n          '
                        '<tbody>\n\t\t\t<tr>\n\t\t\t\t<td '
                        'style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:20px 20px '
                        '10px 20px;">\n\t\t\t\t\t<!--[if mso | IE]><table role="presentation" border="0" '
                        'cellpadding="0" cellspacing="0"><tr><td style="vertical-align:top;width:600px;"><!['
                        'endif]-->\n\t\t\t\t\t<div class="mj-column-per-100 outlook-group-fix" '
                        'style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left'
                        ';width:100%;">\n\t\t\t\t\t\t<table role="presentation" cellpadding="0" cellspacing="0" '
                        'style="vertical-align:top;" width="100%" '
                        'border="0">\n\t\t\t\t\t\t\t<tr>\n\t\t\t\t\t\t\t\t<td>\n\t\t\t\t\t\t\t\t\t<h2 '
                        'style="color:#263640;letter-spacing:0.25em; font-size: 18px; line-height: 25px; text-align: '
                        'center;">Report - Bandwidth Utilization '
                        'report</h2>\n\t\t\t\t\t\t\t\t</td>\n\t\t\t\t\t\t\t</tr>\n\t\t\t\t\t\t</table>\n\t\t\t\t\t'
                        '</div>\n\t\t\t\t\t<!--[if mso | IE]></td></tr></table><![endif]-->\n\t\t\t\t</td>\n          '
                        '\t<tr>\n              <td '
                        'style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:10px 20px '
                        '40px 20px;">\n                <!--[if mso | IE]><table role="presentation" border="0" '
                        'cellpadding="0" cellspacing="0"><tr><td style="vertical-align:top;width:600px;"><!['
                        'endif]-->\n                <div class="mj-column-per-100 outlook-group-fix" '
                        'style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left'
                        ';width:100%;">\n\n\t\t\t\t<!-- DATA TABLE -->\n                  <table role="presentation" '
                        'cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%" border="0">\n       '
                        '             <tbody>\n                      <tr>\n                        <th '
                        'bgcolor="#263640" style="background-color: #263640; color: #ffffff; font-weight: bold; '
                        'font-size: 16px; line-height: 22px; padding: 15px; letter-spacing: 0.05em; border: 1px solid '
                        '#DDDDDD;">Serial Number</th>\n\t\t\t\t\t\t<th bgcolor="#263640" style="background-color: '
                        '#263640; color: #ffffff; font-weight: bold; font-size: 16px; line-height: 22px; padding: '
                        '15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD;">Client ID | Name</th>\n            '
                        '            <th bgcolor="#263640" style="background-color: #263640; color: #ffffff; '
                        'font-weight: bold; font-size: 16px; line-height: 22px; padding: 15px; letter-spacing: '
                        '0.05em; border: 1px solid #DDDDDD;">Location</th>\n\t\t\t\t\t\t<th bgcolor="#263640" '
                        'style="background-color: #263640; color: #ffffff; text-align: center; font-weight: bold; '
                        'font-size: 16px; line-height: 22px; padding: 15px; letter-spacing: 0.05em; border: 1px solid '
                        '#DDDDDD;">Number of tickets</th>\n                        <th bgcolor="#263640" '
                        'style="background-color: #263640; color: #ffffff; font-weight: bold; font-size: 16px; '
                        'line-height: 22px; padding: 15px; letter-spacing: 0.05em; border: 1px solid '
                        '#DDDDDD;">Tickets</th>\n                        <th bgcolor="#263640" '
                        'style="background-color: #263640; color: #ffffff; font-weight: bold; font-size: 16px; '
                        'line-height: 22px; padding: 15px; letter-spacing: 0.05em; border: 1px solid '
                        '#DDDDDD;">Interfaces</th>\n                      </tr>\n                      \n             '
                        '           \n                        <tr>\n                          <td class="even" '
                        'bgcolor="#FFFFFF" style="background-color: #FFFFFF;\n                          color: '
                        '#596872; font-weight: normal;\n                          font-size: 14px; line-height: 20px; '
                        'padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD;\n                          '
                        'white-space: nowrap">VC05200085762</td>\n                          <td class="even" '
                        'bgcolor="#FFFFFF" style="background-color: #FFFFFF;\n                          color: '
                        '#596872; font-weight: normal;\n                          font-size: 14px; line-height: 20px; '
                        'padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD;\n                          '
                        'white-space: nowrap">83109 | RSI</td>\n                          <td class="even" '
                        'bgcolor="#FFFFFF" style="background-color: #FFFFFF;\n                          color: '
                        '#596872; font-weight: normal;\n                          font-size: 14px; line-height: 20px; '
                        'padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD;\n                          '
                        'white-space: nowrap">621 Hill Ave<br>Nashville<br>TN<br>37210-4714<br>USA</td>\n             '
                        '             <td class="even" bgcolor="#FFFFFF" style="background-color: #FFFFFF;\n          '
                        '                    color: #596872; font-weight: normal;\n                              '
                        'font-size: 14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid '
                        '#DDDDDD;\n                              white-space: nowrap">4</td>\n                        '
                        '  <td class="even" bgcolor="#FFFFFF" style="background-color: #FFFFFF;\n                     '
                        '         color: #596872; font-weight: normal;\n                              font-size: '
                        '14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD;\n '
                        '                             white-space: nowrap">5081250,<br>5075176,<br>5074441,'
                        '<br>5073652</td>\n                          <td class="even" bgcolor="#FFFFFF" '
                        'style="background-color: #FFFFFF;\n                              color: #596872; '
                        'font-weight: normal;\n                              font-size: 14px; line-height: 20px; '
                        'padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD;\n                          '
                        '    white-space: nowrap">GE1</td>\n                        </tr>\n                        \n '
                        '                   </tbody>\n                  </table>\n\t\t\t\t<!-- END DATA TABLE -->\n\n '
                        '               </div>\n                <!--[if mso | IE]></td></tr></table><![endif]-->\n    '
                        '          </td>\n            </tr>\n          </tbody>\n        </table>\n      </div>\n     '
                        ' <!--[if mso | IE]></td></tr></table><![endif]-->\n\t<!-- END DATA TABLE -->\n\n\t<!-- START '
                        'FOOTER -->\n      <!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" '
                        'cellspacing="0" width="600" align="center" style="width:600px;">        <tr>          <td '
                        'style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;">      <![endif]-->\n     '
                        ' <div style="margin:0px auto;max-width:600px;">\n        <table\n          '
                        'role="presentation"\n          cellpadding="0"\n          cellspacing="0"\n          '
                        'style="font-size:0px;width:100%;"\n          align="center"\n          border="0"\n        '
                        '>\n          <tbody>\n            <tr>\n              <td\n                '
                        'style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:0px 0px 10px '
                        '0px;"\n              >\n                <!--[if mso | IE]><table role="presentation" '
                        'border="0" cellpadding="0" cellspacing="0"><tr><td '
                        'style="vertical-align:top;width:600px;"><![endif]-->\n                <div '
                        'class="mj-column-per-100 outlook-group-fix" '
                        'style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left'
                        ';width:100%;">\n                  <table\n                    role="presentation"\n          '
                        '          cellpadding="0"\n                    cellspacing="0"\n                    '
                        'style="vertical-align:top;"\n                    width="100%"\n                    '
                        'border="0"\n                  >\n                    <tbody>\n                      <tr>\n   '
                        '                     <td\n                          '
                        'style="word-wrap:break-word;font-size:0px;padding:20px 0px 0px 0px;"\n                       '
                        '   align="center"\n                        >\n                          <div\n               '
                        '             style="cursor:auto;color:#000000;font-family:\'Roboto\', Helvetica, Arial, '
                        'sans-serif;font-size:14px;line-height:1.5;text-align:center;"\n                          '
                        '>\n\t\t\t\t\t\t\t  <p style="color:#596872; font-size: 12px;line-height: '
                        '18px;"><unsubscribe>To unsubscribe contact '
                        'mettel@intelygenz.com</unsubscribe></p>\n\t\t\t\t\t\t\t  <p style="color:#596872; font-size: '
                        '12px;line-height: 18px;">© 2019 Intelygenz Software: All rights reserved</p>\n               '
                        '           </div>\n                        </td>\n                      </tr>\n              '
                        '      </tbody>\n                  </table>\n                </div>\n                <!--[if '
                        'mso | IE]>      </td></tr></table>      <![endif]-->\n              </td>\n            '
                        '</tr>\n          </tbody>\n        </table>\n      </div>\n      <!--[if mso | IE]>      '
                        '</td></tr></table>      <![endif]-->\n      <!--[if mso | IE]>      <table '
                        'role="presentation" border="0" cellpadding="0" cellspacing="0" width="600" align="center" '
                        'style="width:600px;">        <tr>          <td '
                        'style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;">      <![endif]-->\n     '
                        ' <!--[if mso | IE]></td></tr></table><![endif]-->\n\t<!-- END FOOTER -->\n    </div>\n\n  '
                        '</body>\n</html>',
                'images': [{
                    'name': 'logo',
                    'data':
                        'iVBORw0KGgoAAAANSUhEUgAAAGQAAABGCAYAAAA6hjFpAAAAAXNSR0IArs4c6QAAC7ZJREFUeAHtXH9wVEcd3317kJQf'
                        'MoDo0HZKhOQOgy0/khxlDMkFRZ0OU8SUHx1+lGIrrR2nnXGsWouEKhYo1QqoU/9hWjq1QsVWEaMjyV1ipblLphQNkuOoq'
                        'aW1EHCgQEqSe2/97Lvbl3fv7iUh10nei7fDsbvf/e6v72c/++u9PEJc7rz+wGZ0QXF5N4zmMyPkwkBhyaIZlGovT76x4K'
                        '0L77193IVdSGuyq0eWomg1lFKFUDpiWOJahiTZ8UsAAkcmTZ467fRIYIlrGWKwQ5J+hLDElQwxs6MXj5HBElcyhCnaFsxT'
                        '6W0fASxxHUMysWMksSR9lMneOdS3ZYdsr8tZ4iqG9MWOXjzcvZa4iiH9sqMXFdeeS1zDkIGwoxcP97LENQxhTH0i485Kom'
                        'D1XbqWuIIhCXbwZwEItdrdLu7W07srGHLd7JAouZAljmdIf+zgnHSBDR6Jgdl3I0scz5D+2KFRuhQgXDEDkRJ2GUscDYhg'
                        'BxiwKsXApggnvC4Wrv8T4eQZkzglCJbM8JZWrk4ROjjiaEAUpv6gr50VV5XHhG27esjT8EYESxwLiGAHRv5Ku8Es2HGqpb'
                        '5JpLcfC14cKSxxLCADZYcEbKSwxJGAXA87JCA6Swj5qYxbfbesJY4E5HrZIY3f1U12IuzqtcRxgAyGHRIQwRKsLbtk3Oq7'
                        'gSWOAwTPyn84kJ2V1dgy3t1Nn0LYtSxxFCA6OwhfIY1r9c07K2uajLudJY4CJFt2SFDczBLHAPJRsEMCorOE890ybvWdvJ'
                        'Y4BpCPih3S+N09dAfCrltLHAFI0byKT5Ms1w4JhPTdyhJHAEKZsjmbnZUEweq7kSXDDohgB+b0Ad1ZWQ0u4p+au2haJrmQ'
                        'JVhC9tilO3EtGXZABDvsDCbk8kY3o04g4BnlUeuml5TfkjEdwu4esh2ea9aSYQUkW3Z4O8l6THXTRzGPfg2fCRS3sWRYAc'
                        'mWHZTzTQIETsh9/bEEOtcyAabLHPRUcdgAyZYdvk5yD/5QR5+q8CoKA0u+a2dwwRKg5oqb4GEDhDJaY2dAIe9v7SCcfz8l'
                        'P+cbppUsnJoiM0c0stMNLBkWQBLsoIO+s/Jd0dZJdhg2p3R0vqLoU5ghMwWiLcHzbmDJsACSNTsSc77J3Ebwq25nyZADki'
                        '07iq7ytWnskHiAJXmK8riMWn3BEurw5yVDDki27ECDa6yGNsexwN/XF0u4Sp9y8loypIBkzw6yxpYdEhWdJex7Mmr1nc6S'
                        'IQVE8dAtVgOZ433urPC1BoXwPvPLsjAt3e9WlgwZIIIdhNDl0mhWv7+ngV5/wH7tsBYmWMKY7ek9yRJHPi8ZMkCyZQe2rL'
                        'ZbWiseIo5T/Nf6YckOJ64lQwJI9uyoWCNuZjMZ3lams0SxPb07lSUZX+O37eQgE3BndQdGeMguu0aJ7VZVz8NpOXzb/Hbl'
                        'AkTfzQsW3HDm6NEPM+lgx7UDf+1ehjSaKR1SUe++jGk5Yc4COQvkLJCzQM4COQvkLJCzQM4COQvkLJCzQM4COQv8H1iA+v'
                        'yBX+CFge62SOhh0V9faZWvrbm+zb7vy5nX37EJVyHXopHgNq+/ajZeSVhmry8u+rQTbZGG/V5/JfQo9DM4jXREm4M/EylF'
                        'pYGNuNKYSlSyR9w5SW1vaeAhfDJ5CtXoG2jjq1Iu/Rmlgc8whdyFOKeXen7c1vbaZVJSMsrLxi2hnKznlBYj7Wb0V3zjt7'
                        'a7gz7Z3h40Xg+65dbyifk3eHQ7yDLNvsbpgVikvlW8Lcku570fi/2xy5xuDheVVlVThd+KPryEPpwsnL+wWOHM9j0CPS/n'
                        '58Rd1gNoqGhUoiGUb/WWBdph7Ech03RF03+FhVc8uPjZjJvSSxBvQ9/niLhJJS3ICT0I4X6Y6Su4X1qTpgABV/g/4emAUM'
                        'o3UkLnalz7NWQGIHg4dZJwbTcQjmMglEXD9W/Ksny+z44HWL9HvACDZacAo3D+/I8pWv5fUFaZuK3Cv4Sj1I+AP28KWTlj'
                        'SsXi05GGd0RCfj6Z2FdfGFFPQK11NIvP5pO0VwvnB5bEmoJnRF6rQx/uQlmrOCPHkHaSqKwYg6xPO6GBK9IuF/FcAi8D0m'
                        '9iNM/FH75U6+80WWszxXsoq2WqWiVFGKF7ES7QiLaaa8p7upwqHTJd+ACzRtNSLwsVSq6adTKFo5H6IxgsO9Dwb+Mh1CsA'
                        '4TadBaLMCaP2wQAFnPNIdCwVt7wK0/JrAaK4PHyba+Q7UX75N6JcLx1fDVC3AqJTAONdIbO4dlUj91pkhKi8VcpQ12ymkW'
                        'NJUF6XcltfVUMqYYadhB7jnHJGRbtvgt0PR8OhA2mAyAIxqhbljSbHMIV9sa8p7F9NR84ij/jpDkB2Ii/eq/I0xVrqTku5'
                        '2UfqiVhzKGiWDTQcHUse917lVRg0fgEC8n3ZVxp4BP5SfIbjIulmy0ikDgyqWAeDLwD4MUxf86Ji+kq6KCEvTZkVOPQJ0t'
                        'ENUdosAON0Dqh9lExmnDRiKn1ETreyDqsfe6NRDMqgWe4tq/y6AAPD6b/qtZ57RZrt8xA0SlxZT8NIainyB5aYCxrWcDAY'
                        '1xRaLYyPziz1lVX+HL14CszgiN8dfbNOH/GU0wf0dmpkk2SRud0drcErra2tApBBu6SNPJiK9mAgPk/w8vdAC/POXnQTBt'
                        'V2oa8R/o3Tx/92ToTtC9DoBszr9yPTIjx9+x0eoW6JhoNbRKZsnZiyfGVYoJMOHauLRkJPyHh/vpi3vaUVqwlV/oAp6cGk'
                        '/pNtkWCtzAt08GkOzi9154l1xXCodw3SCg1BMqD1qFi/0DI4bAAKoBfUI8n/erT4urda/vpvswwD4BCM2YgZ4Sf4rcXL30'
                        'Xa3IV3JtlgVk0Pj1b3oqZx6PvhU+GGF6WCPSBE+yAabljs81duAyjfQoYazN+lnZ6L94xV82T+QflofDFmtV7H6fu9kYGF'
                        'os0Nh7FDfBbaG2H3MABNecgFo44DWPTs8T+nPpyifC3q/4K1ljhnz4wm8YSY0jEIVJp1PMQjZGnuVDi0G+w4hqX3t9iw3M'
                        '487Dg2HF/CYEjTlQJMcauguxgql9SuxFQl0/oARFfR2sKhR4vKKl6nRHkRhSwZE897LcWYsqTr8vkKlHvgurJkUta0MN5'
                        'F2YikZvwsawGNQFaJtpefijQ0GNk53QeGHNXjnHwcfXoIpjsrNi/esvJJQo5RewIL7CwjTz8B6DZicZ+jaKQW5c0CGE0o'
                        'BVOnedQlCple8vkJlMYTf0REycNyqpJV2K4hUkH46NBBjLb5aPgZVDjTnObcMD8i2oYvkm8VZxHZTkxrL2DqrRE/sfcQco'
                        'zUX8n0wfpiGu30dJWBrQdhozyQc3qmsjysZxfqnYw6j6ANz1l1+mOIoS/2/DP9n5ujEfUQcL/dSBhEAOeS4sLSQMCcVaH8'
                        'KqYdMaoNRz2kDHqfNAQiwNRzsaZGcR7o03k6z2+Pj52yAW0tx8HwFczt6+XcDibAWJ5NSFsPRK5RjWw1F4YpbYy1fXq6qr'
                        'bKMsz6Mpx8dl+ND6Y9BqOLL1Kgil5XVFq5GGWvA2ggKd1rrcPDtQsDBkQUezJ85AJGW4WPjRffE7m7t6rrC6GVNTivpDgY'
                        'RhwMxUnacJgmn7PqEc5ehsJyQ8kmIHZQM0sq7uQKPQS73ME8yrvYmJxA3ROQpUDPxskFrODLoi2h3sNnorwC1FufCJr+p3'
                        'QlYvtNkozBaHPoR4X+qhaFaNBNYCJetqAq3SsyJIF6gSWSjDI4V2o9MIQ47RrXBwj/A0QGpdgFQ9McaGnpaSPkwSJ/RaNZ'
                        'bIQ5DSPcwbSu1MVUKHBxGqchQzclQNtN0Wa04QNT3AhiaBmHMzDtP1i8QxhtOFqku5MtDX/HnH3bKBbfhnqxmBP92gZ9Po'
                        'vZ6nlVobtiTaEzMmeXRj/MV1IPrDJN+CpXzgk/Tsl5GC6EI7TRFiE3O/HpQXwMYR5j2kQhHxvPq4YXS/6EKN1RftyCUbrO'
                        'SJHcWFIyZjwbX9xN2TvJw6wju/Y/KWSv3s4YAHAAAAAASUVORK5CYII='
                },
                    {
                        'name': 'header',
                        'data': '/9j/4QAYRXhpZgAASUkqAAgAAAAAAAAAAAAAAP/sABFEdWNreQABAAQAAABQAAD/7gAOQWRvYmUAZMAAAAAB'
                                '/9sAhAACAgICAgICAgICAwICAgMEAwICAwQFBAQEBAQFBgUFBQUFBQYGBwcIBwcGCQkKCgkJDAwMDAwMDAwMDA'
                                'wMDAwMAQMDAwUEBQkGBgkNCwkLDQ8ODg4ODw8MDAwMDA8PDAwMDAwMDwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwM'
                                'DAwMDAz/wAARCAEYAlgDAREAAhEBAxEB/8QBogAAAAcBAQEBAQAAAAAAAAAABAUDAgYBAAcICQoLAQACAgMBAQ'
                                'EBAQAAAAAAAAABAAIDBAUGBwgJCgsQAAIBAwMCBAIGBwMEAgYCcwECAxEEAAUhEjFBUQYTYSJxgRQykaEHFbFC'
                                'I8FS0eEzFmLwJHKC8SVDNFOSorJjc8I1RCeTo7M2F1RkdMPS4ggmgwkKGBmElEVGpLRW01UoGvLj88TU5PRldY'
                                'WVpbXF1eX1ZnaGlqa2xtbm9jdHV2d3h5ent8fX5/c4SFhoeIiYqLjI2Oj4KTlJWWl5iZmpucnZ6fkqOkpaanqK'
                                'mqq6ytrq+hEAAgIBAgMFBQQFBgQIAwNtAQACEQMEIRIxQQVRE2EiBnGBkTKhsfAUwdHhI0IVUmJy8TMkNEOCFp'
                                'JTJaJjssIHc9I14kSDF1STCAkKGBkmNkUaJ2R0VTfyo7PDKCnT4/OElKS0xNTk9GV1hZWltcXV5fVGVmZ2hpam'
                                'tsbW5vZHV2d3h5ent8fX5/c4SFhoeIiYqLjI2Oj4OUlZaXmJmam5ydnp+So6SlpqeoqaqrrK2ur6/9oADAMBAA'
                                'IRAxEAPwCd5hPzu7FXYq7FXYq7FXYq7FXYq7FXYq7FXYqsOKtZJIaOTCVM5IJaOFVlckyccmhYckEtYQkLGOTC'
                                'VuSZNfq74QrWTCrGOTCQsySVpwpW5IKHHJBkpnJK0emTCrDhCVo6ZIJaySuOTVTJ+/JMmjkgqw5JVuSDNonJJW'
                                '4QhaxyYSFM5Nk1hVYckFdkgyC09ckErcmErCckENdsLJb3yQVo+OSVYcmyW5IBVhyQStwpDRNMkGSw75MK0cmF'
                                'UzvhZBxySrRklaOSZBaeuSCVpyYCVuSULThDJYckENHJhK05JKw5IJWnJKtwhkHvWeBPIOxV2KuxV2KuxV2Kux'
                                'V2KuxV2KuxVo4qswhWskGS0/LJqswpWnJBIaH6skElaT92TCrfwyQVxyQZKRyQSHHClbklaOTVTJyYSGsKVM5I'
                                'KXZJkFpyQStyQVaTkkqZySXHb3yQVrJBVp75MJCzJBLROSCVn0ZJaa98kGSzCl2TQpk5MMgswpWnCFW5NIdkmS'
                                '3vkgq05MJWdTklDRwsmskELDkgkLcklacmEqZySuwhkFpPXJBKzJhVpOTStwhLRyQVrtkkhaflkmS3JBK05MKt'
                                'wpC0/hkkrckELScmErMIStOTSsOFXZIM3vWeAvHuxV2KuxV2KuxV2KuxV2KuxV2KuxVacVW5IJDRyQSpnJBLWF'
                                'VhybJ3QeByYCFhwhLWSCQsbJhK33wpaOSCWumSCrGP4ZMKFmTZNHCErMkEOyQZrDklW5IBVhOSDJaMkFaOSVxy'
                                'QVYcmGS04Qqwn2yaWjhZLTk0rcIQ0TkgoUj1ybNrpklWH/ayQVrJBIaJwhk1kwqwnJhK3phStOFWsmqw5NK3C'
                                'AlYcmErcKhrCGaw75YArWSCqZOSZOO2FVuTCtHJBkFpwhK05MJWnJhQ0cIZKZyQQ7JBVhybJYcIVaTk0rcISG'
                                'ickGRe954A8e7FXYq7FXYq7FXYq7FXYq7FXYq4nFVM9emIV2TSFhySVmSS0cIStG+TCWickFWZIK45IMlM5MK'
                                'GsLJbklDvHJhVInfJBIaySVh/HCFLWTSGjkgyWHJBVpOSSpnJJd0yQVrvkgq05IJC3JJWk07ZMJWZJQ7JBksOF'
                                'LWSCFjH23yYZBTySWjhVbk1DWSDJbhCWjkwlYdz8smoWn9WFk1hCFpyYVZkmS05MJWHCrWSZBacklZkwrROSCV'
                                'nfClo5IK103ydKtrhZhbkwErTkwq3CkLTklW5IKtOTASFpPen0YUrTk0rDhVrJBkFjHJBXvufP7yDsVdirsVdi'
                                'rsVdirsVdirsVdiq0nFVuSChrJBksPyyShbhSsOTDINdBkghackEte+SSFrZMJWZIJaOEK1kkrScmqnk2TROKV'
                                'mSCHZIMgFh/HJJW5MKtJyQSswpaOSV3QZMKsPfJhktwhVpyaVpwpC05MJW4hWjkwlSOTZBrpklWn5YQq3JBIaJ'
                                '9skyayYVYckFW5JkFpwq1k1Wk5IJWZIJWnJBKzJKHYQzCw/7WTCrcmFWHvkkhrxwpW9T8skFcfDwyQSFhyTJo5'
                                'MJWZKlaOSCQsOSCtZIKsOTZLThCrTkglZ9GSCQGjtkgyUzucmFD3/AD59ePdirsVdirsVdirsVdirsVdirjiqw'
                                '4oayTILTk0qeSS0cISt6nJhLjklUzkgrskEhYT7ZMJC3CyWnrkgodkgpU2O+TASFuSSsOFLWSCgNHvkgyWHJK0'
                                'cmqmckya7YQrX+ZyQVo5NIWZJLRyQSFPJK7JBksJySWskELGOTCQsyTJacKrTkgrWSDILTkgEtH2yYSsOSVrph'
                                'CVmSCtH3yQVYcmya6ZIKsPyyQStwpDRyTJT75YFaP4ZIKs64WTjklWjJK1kgzCzJBLRyYVbkkhacklZkgrRyQV'
                                'ZkkrTkgqw5JLWSDILG/HJBVvj+GTDJ7/nz48c7FXYq7FXYq7FXYq7FXYq7FWjiqzCFaOTDJYckoW4UrTkgyDQy'
                                'YVackFW++SCtE5IMlPvkgkOOFK3JJaOTQpZYyaOKrDvkgrskGQWnJBK3JBVhOTCVnXthS0ckrskFWHJhK3xyQS'
                                'tY/dkglbkkho5IJWYUuOTQpE5NkFuFK05IKtySQ45JktyQVacmFWdckyDRwqtyQVaTkwkLcKVhyaVpyShrCGQW'
                                'HJBLXbJhVhOTSFuFK3vkgFdkgkLDkmTWTASsOSCtdMkkLD8sKtZNVpySVhyQCVuSSsOFQHdPpyQZqZ3yYUOyYS'
                                '9+z57eOdirsVdirsVdirsVdirsVdiqw4q1kkho5MJUyckEtHCqyuSZOOTQsOSCWskEhYxyQStyTJr9XfCFayYV'
                                'YxyYSFmSStOFK3JBQ45IMlM5JWj/t5MKsOEJWjpkglrJK45IKFMn78myaOSCqZySuyQZrScklbhCFjZMJCw5Nk'
                                '1hVYckFdkgyC09ckEre2TCVhOSCGu2Fkt75IK0fHJKsOTZLckFWHJBK3CkNE0yQZLDvkwrRyYVTO+FkHHJKtGS'
                                'Vo5JkFp65IJWnJgJW5JQtOEMlhyQQ0cmErTkkrDkglackq3CGQWtkglZkwFaJyaQ+gM+enjnYq7FXYq7FXYq7F'
                                'XYq7FWjiqzCFayQZLT8smqzClackEhofqyQSVpyYVbkgrjkgyUjkgkOOFK3JK0flk1UycmEhrClTOSCl2SZBac'
                                'kErckFWk5JKmcklx298kFayQVae+TCQsyQS0TkglZklDXvkgyWYUuyaFNjkwyCzClacIVbk0h2SZLe+SCrTkwl'
                                'Z3ySho4WTWSCFhyQSFuSStOTCVM5JXYQyC0nrkglZ45MKtJyaVuEJaPXJBWu2SSFp+WSZLckErTkwq3CkLT+GS'
                                'Vbkgq0nJhKzCErTk0rDhV2SDNTJ/tyYUO6ZMJWHCofQOfPTxzsVdirsVdirsVdirsVdiq04qtyQSGjkglTOSCW'
                                'sKrDk2Tug98mhYe+EJayQSFjZMJW++FLRyQS10yQVYx/DJhQi9MsJ9V1LT9LthW51K5itbceLzOEX8Tkjs3YsZ'
                                'yTEBzJA+b7DP/OF3mc/9Nppf/SPP/XKRnHc9n/oJzf6pH5Faf8AnC3zP/1Oul/9I8/9cP5gdy/6CM3+qx+RUbn'
                                '/AJwx80w29xMnnDTJ3hjZ1hW3mBcqCQo9z0wjUjuRL2LzAE+JH5F8XnMx4xbkgFTDRtI1DzBq+maHpcBudS1e5'
                                'itLKAftSSsEWp7Cp3PYb4SQBZbsOGWacYQFkmg+wv8AoSnzRsf8baXX/mHnzE/Ox7nsP9Beb/VI/Iu/6Eo80f8'
                                'AU7aX/wBI8+S/PR7k/wCgvN/qsfkWOebv+cTNe8n+V9e80X3nLTZ7XQbKa8kgSCYPJ6akrGpOwLmgGWQ1glIRA'
                                '5uPq/ZPJpsMssskaiCeRfIxzPeUaOEKsJ9smlrJBkFpySVuEIaJyQUKR65Nmm/l7RrnzHr+h+XrMhLvXb+20+2'
                                'dgSokuZViUmnYFt8E5iETI9A24MJzZI4xzkQPmafZB/5we81H/pudJ/6Rp/65qx2xD+aXrP8AQdl/1SPyLX/Qj'
                                '3mv/qedJ/6R5/65L+WYfzSkex+X/VI/ItH/AJwd81/9TzpP/SNPh/lmH80p/wBCGX/VI/Itf9COea/+p50n/pH'
                                'nw/y3D+aV/wBCGX/VI/IsA/Mz/nFrW/yy8m6p5x1Lzdp1/b6a1ugsYIZUklaeZIQqlttufI17A5k6XtSOfIICJ'
                                '3cLtD2dno8JyymCBW1HqafK3TNs88tOFWsmrccUk8scEKGSaZ1SJB1ZmNAB8zkuTKIs0H3EP+cF/NhALeedIDU'
                                '3H1ec0OaH/RBj/mF67/Qjl/1QfIsS89/84i6/5C8oa95v1DzpplzZ6DbG4ktooJleQ8giIpY0BZmA3zI03bUM2'
                                'QQEDZLj6v2bnpsMsspgiI7i+P8AN480GjkgzWHfJhWskFUyckycdsKrcmFaJyQZBacIStOTCVpyYUNHCGSmckE'
                                'OyQVYcmyWHCFWk5NK3CEhonJBkVnXJhWicmEqZ64UvoPPnl412KuxV2KuxV2KuxV2KuJxVTxCuyaQsOSSsySWj'
                                'hCVg/28mEuJyQVZ1yQVxyQZKZNcmFDWFktySh3jkwqkckGQeufkLo36c/N7yLZleaW+ojUH8ALBGuhX6YgMGQ1'
                                'Eu49n8Hja/FHulf8ApfV+h+wWYL7K7FXYq/Dnzfpn6F82eZ9H48f0Tq17ZhfD0J3jp/wubeBsAvhusxeFnnDuk'
                                'R8jTHCcsaH29/zh5+W/1zUtS/MvU7etvpZfTvLYcfauXX/SJ1/1EbgD0PJu65iazJtwvcex/Z3HI6mQ2G0ff1P'
                                'wG3xPc/QvNe+guxV83/8AOVutfon8m9YtlfhJr17ZadGehP70XLgfNIGB9sy9FG8g8nnfanN4ehkP5xA+2/0Py'
                                'dzdPla0mnbJhKzJK144QyWnJJayQQ9F/Lb8qvN35qax+i/LVj/o0BU6prU9VtLRG7yOAasf2UWrHwoCRXn1EME'
                                'bl8nZdndmZtdPhxjbqeg/Hc9n/wCch/yz8pflB5X8ieVdEX9Ia7q091f6/wCYJ1H1ib6ukccaqNxHGTM9EXw+I'
                                'sRXMbQ6ieeUpHkOQdx292dh7PxY8UN5GyT1NfcNzt87YD/zjXpkGp/nP5NN06RWmmSz6jPLIwVVNtbyPFuaD+9'
                                '4DL9fKsMq67OF7P4xPW475Cz8ht9tP1+TVNNkZUTUbV3chURZkJJOwAAOcvwnufU/Ej3hH4GanLLHBG0s0iRRp'
                                '9qRyFUdtydsQLQSBuUH+ltK/wCrnaf8jk/rkuCXcx8WHePm+N/+c0/M9ov5e+XdCs72KaXV9bWedYpFesNpBIS'
                                'CFJ/blQ/Rm47FxHxTIjkPveW9q9QPy8YA85fYB+0PzJP6s6h4FrCELTkwr0n8mtE/xH+a35f6QU9SKbW7Sa5Tx'
                                'htpBPKPpSNsx9dk8PBM+Rdj2Xh8XVY4/wBIfZuX7kZwL60+Uf8AnMnW/'
                                '+j9LzvtPl4NHw/zpAfp/Q/JPO1fOwtOSSsyYVonJBKzClo5IK1k6VbXCzC3JhVpyYStwpC05JK3JBC05MBIWk'
                                '96fRhStOTSsOFWskGQWMckFa6ZMMljHrklDQyQS+gs+eHjXYq7FXYq7FXYq7FXYqtJxVbkgoayQZLDklC3ClYc'
                                'mGQa6DJBC0/hkglrJJWtkwlZkglxPthCrcklonJqpZNk+tP8AnDzRvrv5i6xq7pyj0TRZRG/8s1zLHGv3oJMpz'
                                'nZ6/wBjMHFq5T/mx+0kfot+leYj6cwmPzQr/mJeeSwwJg8u2+s8dqgyXUsB3+SrtkuH035uCNVeqODugJfaQzb'
                                'Iuc/Hz/nIPTP0T+cnnu248VmvkvR7/XII7gn75Dm105uAfH/aHF4evyjzv/TAH9LzHy9oOpeade0ny7pEPrajr'
                                'N1HaWib0DSNTkx7Ko3Y9gCcuMhEWXW6bTz1GSOOHORoP2q8m+VdO8k+V9E8q6UtLLRbVYEkpRpX+1LKwH7Ujln'
                                'Puc005GRJL7To9LDS4Y4ocoiv1n4ndLdU81rF568s+SbFlkvr20u9Z1pepi0+3Uwxk+BkuJEofBGGSEPSZNWXV'
                                '1qIYI8yDI+URt9siPkWc5W5z4U/5zb1r09M8ieXUev1q5vNRuI/D0EjiiJ+frPT5Zsuz47kvD+2maoYsfeSflQ'
                                'H3l8ZeQvy283/AJk6qNK8q6U92yEfXtQkrHa2qt+1NMQQvQ0Aqx/ZBzPyZY4xcnj9B2dn1s+DFG+89B7z+C+3v'
                                'KH/ADhd5btIoZ/O/mS81i82aSw0ylrbA/ymR1eVx7jh8s1+TtGX8Ip7XSex2KIvNMyPcNh+s/Y9fg/5xj/JCGE'
                                'w/wCCFm5D4pZL6/Zz/svrG30Uyg63N/O+528fZvs8CvD+2X63n/m7/nDn8u9XtpG8qXl95R1AA+iDI19an2eOd'
                                'vV+kSj5HL8faOSP1buDqvZLTZB+6Jgf9MPt3+1+ePn3yH5h/LnzJeeWfMtr6F7bUe3uEqYbmBieE0L0HJWp8wa'
                                'ggEEZuMOWOWPFF4LXaLLo8px5BuPkR3h7f+Sf/ONOv/mO1r5g8y+t5e8lHi8UxHG71BetLZWB4oR/uxhT+UNvx'
                                'x9Vro4vTHeX3O57G9ncmsrJkuOP7Ze7y8/lfT6eeWvLGg+T9HtNA8taXBpGk2YpDaQLSpPV3Y1Z2am7MST3OaH'
                                'JklkPFI2X0fT6bHp4CGMARDzP8y/yI8lfmtq1hrHmi41VLnTbQWdrFZXCRRBPUaQsVaJzyJahNegGZGn1k8AIj'
                                'W7r+0OxcGumJ5DKwK2P7HnH/Qmn5Rf8tHmD/pNi/wCyfL/5VzeXy/a4H+hPR98vmP1Jx5c/5xQ/K3yxr+jeY9P'
                                'k1qW/0K8hv7JLi6jeL1rdxJGXUQKSAwB65HJ2nlnExNUQ24PZnSYckckeK4kEWe74PpnNe9C+Wf8AnMHW/wBFf'
                                'k5c2AajeY9WsrAr3Kxs14fo/wBHFc2fZEOLPfcD+r9LzntRm4NGY/zpAf779D8tPL/lzXfNerWuh+XNKuNZ1a8'
                                'alvZWy8mI7sT0VR1LMQAOpGdTPJHHHikaD53gwZM8xDGCZHoH3J5F/wCcI5ZYorz8xfM7WzuAzaJogVnSu9Hup'
                                'lZajoQsZHg2aTP230xx+J/V+17DR+yRIvPOvKP6z+r4voTT/wDnFX8jrCJUk8nvqMoXi1xd396zNtuSqTIgJ9l'
                                'Ga+XaupP8VfAO7h7OaGI+i/eT+tJde/5xA/JnVbWaPTNMv/LV06n0buyvZ5uLdiUu2nBFeoFPmMsx9s6iJ3IP'
                                'w/U1ZvZjRzHpBifIn9Nvz7/OX8jfNP5O6jCNRZdW8u6g5TSfMluhSORgCfSmQk+lJQV41II3VjQ06TQ6+GqG20'
                                'hzDxnafZGXQS9W8Tyl+g9xegf84baJ+lPzjh1EpVfLmkXt8H7B5QlmB8yLg5j9t5OHT13kD9P6HN9l8XHrOL+b'
                                'En9H6X6z5xz6O/PD/nO3XKv+XvlqN/srfandx/MxQwH8JM6f2dx/XP3D8fY8X7W5d8eP3n7gP0vz0zpw8cFjf7'
                                'WTCrcmFWHvkkhrClb1PyyQVx8PDJBIWHJMmjkwlZkqVo5IJCw5IK1kgqw5NktOEKtOSCVn0ZIJAaO2SDJTO5yY'
                                'UOP4ZIJWHJJcdtu2SQ+gs+d3jnYq7FXYq7FXYq7FXHFVh+WKGskyC05NKnkktHCErepyYS4n2ySqZyQV2SCQp'
                                'k5MJDWFktPXJBQ7JBSpsd8mAkLckl+hf/OF2jej5b86eYClP0jqVvYIx8LOIymn/SSMxtQdwH0b2Jw1hyZO+QH'
                                '+lF/759qZjvbvjTQPNf1n/nL/AMzWay1gl0Z9EgFe9tBBdSD6JI3zJMf3QeM0+r4u3Zjpw8PyAl94L7LzGezfl'
                                '9/zl/pn1L81oL0LRdY0S0uS/i8ck1uR9CxLmy0huHxfL/a/Fw60S/nRB+8foej/APOHf5b85dS/M3U7f4YvU03'
                                'yxzH7RFLq4WvgP3YI8XGV6vJ/CHZ+x/ZtmWpkPKP++P6Pm+7NS1Gy0jTr/VtSuFtNP0y3kur66f7McMKl3Y/JQ'
                                'TmEBZoPdZMkccTORoAWfcHyD/zjhrt7+ZH5kfmv+Z18jRpOlppmkQPv6No7u6wim1USCMtTqxJ75mamIhCMA8j'
                                '7OZ5a3VZ9VLyA8h3fYH2ZmE9i/PD8/vLurfmz/wA5B6H5B0VuB03SbWLULkjklrE7Pcz3Dio6RyoAK/EeK982m'
                                'mmMWEyPe+f9u6efaHaccEOkRfl1J+RH2PuPyV5K8vfl/wCXrPy15ashaafaCsjmhlnmIHOaZ6Dk7U3PyAAAAGu'
                                'yZDklZe20ejxaTEMeMUB9p7z5sC/OT869A/KDTLWS8tn1jXtVD/onQ4nEZdU+1LNIQ3pxgmleJJOwGxIu0+mlm'
                                'O2wcHtftnH2dAEi5HkP0nuD5Hsf+c2POK6kkmpeUNGn0cuPUtbZriK5CV3pM8kiE0/4rzYHsyNbE28rD2xz8f'
                                'qxx4fK7+d/ofoD5V8y6X5x8u6P5n0aRpNM1q2S5teY4uobZkcAkBkYFWAPUZqckDCRieYe702ohqMUckOUhby'
                                '7879H8hw6TpH5h+etCn16w/L27F09jawxTvPHd0thG8cskSsizPHKQWp8G4IJGX6SUyTCBridb2zh04hHUZ4mQ'
                                'xm6ABu9upG10fgzn8uvPWkfmP5VsfNehWN7p+k3sk0NpBfxxRS0t5DExCxSSrx5KQPi7ZVmwnFLhPNzdBrYazC'
                                'MsARE8rrpt0JZxlTmPlLXf+cwvyx0DWtY0O50fzJc3GjXtxYz3NtbWbQyPbyNGzRs94jFSVqCVBp2GbKHZeWUQ'
                                'bG/v/U81m9qtLinKBjMmJI2ArbbvSo/85sflX/1YPNf/SJY/wDZdk/5Iy98ft/U1f6L9J/Nn8o/8U4f85r/AJW'
                                'EgDy95sJOwAtLGtf+k7D/ACPm74/b+pP+i3SfzZ/If8U9M8t/nmvm3020L8pvzBuIJaenez6dZWluw9p7m/ij'
                                'P/BZjZNF4f1Th8z+p2Gn7Y8f6MOX30APmZAPnD/nMbU9U8xXH5XeTrHSbq31XVJ7q4XRJTC87TStDbWqj0JZUq'
                                'WMg+1my7HiIccydh1+90XtTkllOHFGJskmtr6AciR3vpf8j/yZ0f8AKPy1FAIorrzXqcSP5k1kCpaTr6ETEVEU'
                                'Z2HTkfiPgNbrdZLUT/ojkHf9kdlQ0OKucz9R/QPIftZv+Yfn/QPyz8r33mvzHKy2dqVit7WKhmubiSvpwwqSAW'
                                'ahPWgALHYHKdPp5Z5iEXM1utx6TEcmTkPmT3B8Dah/znJ50fUWk0ryZottpIc8bW7e5nuCtdv30ckKA0/4rzo'
                                'IdhY63kb+Dxs/a7MZemEQPOyfnt9z7Y/Jz819K/N/ykvmKwtG029tZjZ61pLsHMFwqq/wvQc0ZWBVqDuKVBzSa'
                                '3Ry0uThO46F6vsvtKGuxccRRGxHcUy/Nrybbefvy781+WZ4VlmvLCWTS2YVMd5ApltnB6ikiitOoqO+Q0ec4c0'
                                'Zjv393Vs7S0o1OnnjPUbe8cvtfH//ADgpolIvzC8ySJ9t7HTbST/VEs0w/wCGjzd+0GT6Ie8/j7XmfZHFtkye4'
                                'feT+h+g2c29o/I7/nMbXP0t+dF7YB+S+W9KsdPoOgLo1430/wCkb52vYWPh0wPeSf0fofOfaXLx6wx/mgD9P6X'
                                'yqc3ToFPvlgVo/hkgqzrhZOOSVaMkrWSDMLO+SCWjkwq3JJC05JKzJBWjkgqzJJWnJBVhySWskGQWtkgqzx/DJ'
                                'hk0ckoWDuTkglxySvoPPnZ412KuxV2KuxV2KuxVonFVmEK0cmGS098koWYUrTkgyDQyYVaf1ZIKt98kFaJyQZK'
                                'ffJBIccKVuSS0cmhSyxk0cVfrF/zjLo36H/JzyyzJwm1d7rUZx4+rO6xn6Y0TMPMbk+u+y+HwtBDvlZ+Z2+ynv'
                                '2VPQPyd/LrzX9b/AOckdK8ziT4dd803Yjev7GpvLAgHtSYAZsZx/d15Pk3Zur4u1o5f52Q/7Kx+l+sWa59ZfEX'
                                '/ADlb5G1Lzf5x/KWw0aH1L/zDJeaT6tCVjCNDL6j034ojyOfZTmbpZiMZX0eJ9qtDPU58EYc5XH7j9m5fX/lj'
                                'y7p3lLy9o/lrSIvS07RbWO1thQVYIPidqdWdqsx7knMSUjI2Xr9Lp4afFHFDlEU+Sv8AnMD8yf0ToNj+XWmT8b'
                                '/zEFvNdKHdLGJ/3cZp09WRa/JCDs2ZejxWeI9Hk/a/tLw8Y08TvLeX9X9p+7zZV/ziBon6N/KmTU2Sj+YdYurp'
                                'JO5ihCWyj5Bon+/I62VzruDleyOHg0XF/OkT8tv0F9U5iPUvnj8nNKh1Tzp+cP5kTRiS71jzJPoOl3Tbn6jpIS'
                                'CqH+WR1AP+oMys8qjGHlfzdB2RiGTPqNSecpmI/qw2+39D6HzFd++SfzV/5xgvvzS856h5tvPzFOnR3McNvYaV'
                                '+ijOtrBCgURrJ9cjrVuTn4RuxzPwa4YocPD9v7Hle1PZqWuznKctXQA4boD/ADvi85/6Eb/8yh/3JP8As/y/+V'
                                'P6P2/scD/QX/t3+x/48+v/AMsfJA/LjyNoXksamdYGircD9JGH6v6vr3Etwf3XOTjT1KfaPTNdny+LMyqrer7N'
                                '0X5PTxw3xcN71XMk8t+9iX/ORUkcf5K+f2lICmxjVa/zNcRKv/DEZboheaLi9vkDQ5b7v0hOPyT0X/D35Tfl/p'
                                'hT0nGjW91PH04y3g+tSA+4aU1yOrnxZZHzbux8PhaPFH+iD89/0vQdX1GHR9J1TV7n/efSrSe8n3p8EEbSNv8A'
                                'JcpjHiIHe52XIMcDI8gCfk/BS7upr25uby5fncXcrzTue7yMWY/STnZxFbPispGRJPMoXJoD9Hf+cJfLFmPLXm'
                                'zzZcWUMt3c6rHYWV1JGrSRraQCR/TYiqhjcb0609s0PbGQ8UY+V/j5PfeyOnHhTykbmVD4D9r7pzSvYvlW30iH'
                                'zp/zlZrOq3cX1iy/Kny3ZW1sDuiX9/ymiJHQkRzyEe4Hhm0M/C0YA/jkfkHnI4hqO1pSPLFAD/OO4+wl9VZq3o'
                                '3zv+en5FX350y6BGfO58taZoSTMunDT/rYlnmKgys31qDoqhQKGm+++bHQa8aW/TZPnX6C6TtfseXaBj+84RH'
                                'pV7nrzD5//wChEP8AzKn/AHI/+9hmxHb/APtf2/sdL/oP/wBu/wBj/wAefSP5F/kmPyW03X9PHmU+ZTrtzDcG'
                                'b6n9TEXooycePrz8q8q1qM1uv135og8NV53+gO97I7J/k+Mo8fFxHur9Je6O6RI8jkKkalnY9gBUnNfzdwTT5g'
                                '/5xB0VdM/Jy01FYvS/xNq1/qQUjfisgtF/C32zb9t5OLUV3AD9P6Xn/ZrFwaMS/nEn9H6H1FmoegfhX+b+uf4j'
                                '/NHz/rCv6kV1rt6trJ4wQytFD/yTRc9E0OLw8EI+QfJ+0svi6nJLvkfkNh9jzY5mBwmugyYVYTk0hbhSt75IB'
                                'XZIJCw5Jk1kwErDkgrXTJJCw/LCrWTVacklYckAlbkkrDhUB3T6ckGamcmFDsmEqZOSSHdBklW98kr6Ez51eNd'
                                'irsVdirsVdirsVWHFWskkNHJhKmTkglo4VWZJk49Mmqme+SCuyQSFjHJBK3JMmv1d8IVrJhVjHJhIWZJK0+HfC'
                                'l+3fkvR/wDDvlDytoPDg2j6TZ2ci9PjhhRGJ9yQSc10jZJfctFh8DBDH/NiB8ghvzA1n/D/AJG84a2H4PpmjXt'
                                'xA3T96kDmMD3LUAwwFyAY9oZvB02SfdEn7Nn4x+WdT/Q3mTy/rFeH6J1K0vOfh6EyyV/4XNpIWKfGNLl8LNCf'
                                'dIH5G37l5qX3NBTadZXF5ZahPapLe6aJRYXDCrResAshTwLAUr4bdzjbCWOMpCRG45eV81DWtY0/y/pGp67qs'
                                '4ttN0i2lu72c/sxxKWag7mg2Hc7YREyNBjmzRwwlOZoRFn4PxU8/ecdQ8/ebtc816lVZtWuWkhgJqIIF+CGFT4'
                                'IgC+9K5vMcBCIAfGNfrJavPLLLnI/IdB8A/XP8mtF/wAPflX5C0sp6ciaPb3FxHShWW7X6zID7h5Dmnzy4pk+b'
                                '612Nh8HR4o/0Qfidz97PNX1GHSNK1PVrj/efS7Sa7n3p8EEZkb8FyuIs052XIMcDM8gCfk8Z/5xqmF1+TPlO8Z'
                                'udxey6nPeyd2mfUrkuT9OZGr/AL0/D7nT+zkuLQQl1PET7+IvdsxnePh/Uf8AnNKw03UL7Trj8u7tZ7C4ltpwd'
                                'QQEPE5Rqj6vtuM2cezTIXxfY8Zk9sIwkYnEbBr6u74II/8AOcOlD/ynd3/3EU/7J8l/JZ/nfYw/0Zw/1I/6b9j'
                                'X/Q8Olf8Alu7v/uJJ/wBk+H+Sj/O+xf8ARnD/AFI/6b9jAvzG/wCclF/OTy4v5baX5Sn0S480ajp9s17JeLOK'
                                'C5jdV4CFDu4Xvl+n0PgS8Qm6BcPX+0P8o4vy8YGJkQLu+o8n6SW1vFaW1vaW6+nBaxpFAg/ZRAFUfQBmjJs2+'
                                'gxiIgAcg8h/5yE1dtE/Jj8wbxCQ0+m/UNvC/lS0P4THMnQw4s0R5/du6rt3L4ehynyr/THh/S/F851ofJXZIM'
                                'g/YT/nF7RP0L+SnlLknCfVvrWpT+/1i4k9M/8AIpUzle0p8WeXls+p+zuHw9DDvNn5n9VPoHMB3b5V/wCcd9Z'
                                'h8xedP+cgNaRhJJd+akijfubW39eK2P8AwKnNr2jDgx4o/wBH9VvOdh5Rlz6mffP7BYD6qzVPRvkf80f+cq7T'
                                '8sfO+seTLvyNdanJpa27x6it6kKTJcQRzBlQwtQAuV69Qc2+k7JOoxiYlV+TzXaHtGNHnliOMmq3vnYvuef/A'
                                'PQ9ek/+W4u/+4lH/wBk+ZX8gS/n/Z+1wv8ARfD/AFI/P9jR/wCc7NJ/8txd/wDcST/snw/6H5fzx8v2p/0Xx/1'
                                'I/wCm/YlOvf8AOb1lqmh6zptn5BurK81GxuLa0vG1BHEUs0TIkhUQAniSDSuWYuwDGQJnsD3fta83tYJwlEYyC'
                                'QRz/Y+y/wAo9D/w3+WHkLRinpy2eh2Ruk6UnliWWb/kozZo9bk8TPOXmXqOzcXhabHHuiPnW7JvNWsr5d8seY/'
                                'MDkBND0u71Bq9KW0Ly/8AGuU4cfiTjHvIHzb9Rl8LHKfcCfkH4CSO8jtJIxd5CWdzuSSakk56WBT5ASpHfJhWj'
                                'kwqmd8LIOOSVaMkrRyTILT1yQStOTCVuSULThDJYckENHJhK05JKw5IJWnJKtwhkFpyQSsyYCtE5NIWYQlxyah'
                                'rphS+hM+dXjHYq7FXYq7FXYq0cVWYQrWSDJaflk1WYUrTkgkLR+rtkgktHJhVuSCuOSDJSPhTJBIccKVuSVo5N'
                                'VMnJhIawpZf+Xejf4h8++TdEKc4tS1myhuBT/dJmUyn6EBOCRoEud2dh8fVY4d8h8r3+x+2Ga99vfPX/OUWsfo'
                                'n8m/MMSvwm1mez0+E/wCvOsrj6Y4mGXacXMPPe1Obw9BMfziB9t/cH5O5sw+TP3A8lan+mvJ3lPWOXM6po1jds'
                                '3iZrdHP4nNRMUSH3DRZfFwY598QfmGT5Fynw5/zmJ+ZH1PTdO/LXTLj/SNU4aj5j4HdbaNq28DU/nkUuR1AVez'
                                'ZnaLFZ4i8R7YdpcMBponc7y93QfE7/Ad74J0DSpdd13RdEgr62sX9tYxU68riVYhT6WzZE8IJeDwYjlyRgOciB'
                                '8zT91IYY7eGK3hQRwwIscUY6KqigA+QGc++5AACg8g/5yC1n9Bfk558uw/B7rT/ANHIK7n6/IlqwH+xlJ+WZG'
                                'ljxZY+91Pb2bwtDlPeK/0236Xz5/zhv+YlnLpWp/lrqFwsWo2k8mpaArkD1oJAPXiTpVo2HOnUhieinMrX4TYm'
                                'HQeyHaETA6aR3BuPmOo+HP4+T7nzWvbPlr80/wDnFjyn+Yer3nmTStVm8pa9qD+pqLxwrc2k8n7UrQco2V27l'
                                'XoTuVrUnO0+vljFEWHme0/ZnDq5nJGRhI8+oPw23+Lx6D/nB27L/wCk/mRCkdRUxaUzsR/srpaZkntQfzftdU'
                                'PYw9cv+x/a8V/Pv8iP+VPf4cu9P1O41vR9ZSSG4vp41jMV5EeXCiVAV4yCoJJ+Ft8zNHq/HsEUQ6ftzsT+T+A'
                                'xJlGXXz/s/S8t/Kye2t/zO/Lue8YJaw+ZdKeZ2+yqrdxksfYd8ytQD4Uq7j9zr+zCBqsRPLjj94fuFnJPsbDv'
                                'P/kzT/zC8n675O1SaS3s9bgWNrmIAvFJHIs0UgB2PGRFNO9KZbhynFMTHRxddpI6vDLFLYSH7R9r8iPzm/KXUf'
                                'yf80waDdah+mbK/tFvNL1dYDAJULFHUx85ArIy7jkdiD3zqdJqRqIcQFPl3a3Zcuz8vATYIsGq/SXkQBJCgEkm'
                                'gAHWuZjrX7w+TdFHlvyj5X8vhQv6E0mzsGA8beBIyfpK5xOafHOUu8l9l0uLwsMIfzYgfIIjzNrCeX/LfmDXpC'
                                'BHomm3d+9elLaFpTX/AIHBihxzEe8gMtRl8LHKf80E/IW/L7/nEv8AMu28n/mJe6Nrd0INM8+Rx2r3krUVL+J2'
                                'a2aRj2f1HT/WYdq51Ha2mOTEDHnH7ur577Na8afUGEztPb/O6feR8X6u5yj6Q8L/ADh/IHyh+cAtr3UpZ9F8xW'
                                'EJgs9eswrMY6lhHPGwpIikkgVUipo25zP0XaGTTbDcHo6jtPsbDr6MrEhyI/T3vl1v+cFNREhCfmVbGMHZzpT'
                                'hqePEXR3+nNsO3xX0fb+x57/QfK/70f6X9qW/mF/zh1a+TPy68weZdL80XvmLzDoMIvXtvq8dtbyW0RrcUjDSu'
                                'GSOrj4/2aU32npu2zlzCJiBE7fq7mOt9mBp9PLJGZlKO/KhXXv6eb4x8qaM3mPzR5b8voCW1zVLPT1A6/6TMkX'
                                '/ABtm+zT8PHKXcCfk8vpsXi5Yw/nED5l++iIqKqIoREAVFAoABsABnnL7E8C/5yf1z9Bfkh52kR+M+pwwaZAOn'
                                'L63PHHIP+RRc5suyMfHqoeW/wAg6ft7L4ein50Pmf1W/HC/0vVNLMK6lp11pzXCCS3FzC8JdCAQyhwKggg1Gd5'
                                'CcZ8iC+aTxyh9QI96XeOWhitJyaVuEJaPXJBWu2SSFp+WSZLckErTkwq3CkLT+GSVbkgq0nJhKzCErTk0rDhV2'
                                'SDNTJ/tyYUO6ZMJWHCoa6dskErT1/VkgrRyQSH0Lnzo8Y7FXYq7FXYq7FVpxVbkgkNHJBKmckEtYVWHJsndB75'
                                'NCw4QlrJBIWNkwlb74UtHJBLXTJBVrH78mEhTyaWjhCXpP5P+bdC8i/mDofmzzHa3l5pujfWJPq1ikckzSyQSR'
                                'RkLLJEtFL8vtdsjOJlGg7PsbV4tJqo5soJEb5VzojqQ+4f+hyvyw/6sXmj/AKRbL/stzH/LS8nu/wDRno/5s/l'
                                'H/ingH/OQf5+eW/zV8u6HoPlqw1aySx1E39+dSigjVikTxRhPRnmqf3jVrTL8GEwNl5/2h7fw9oYo48QkKNm67'
                                'qHInvL5MzLAeTfe35af85WeRfKPkPyv5Z13SPMFzqmh2S2dxNZwWrwMI2YR8Gkuo2NE4jdRmHk0spSJFPf9me1'
                                'Wn0+mhinGZlEVsBX3jozg/wDOZ35YUNNB8017A2tl/wBl2Q/Jz7w53+jLR/zZ/KP/ABT88fOnmvUfO/mnW/NWq'
                                't/putXTTtHUssUf2YoVJ/ZjQKg9hmyhAQiAHz7WaqeqzSyy5yN/qHwGyafln5h0Xyn598r+ZfMFvdXWlaFere3'
                                'EFkiPOzxKzRcFkeNTSQKTVht92HLAygQOrZ2ZqMen1MMmQExib257cuZHV98/9Dofld/1YfNP/SLZf9l2a/8Ak'
                                '/J3j7f1Pff6MdH/ADZ/KP8AxTxL8/P+cjvKn5neSYfK/ljTdZsZ31OC6v5dSht442ghSX4FMNxMS3qFDuKUBz'
                                'J0ukljnxSp0vbvtFh12nGLEJA8QJsDkL7ietPj3T9Rv9JvrXU9MvJtP1GxlWazvYHMcsUi7qystCCM2JiCKLye'
                                'PJLHISiaI5EPuPyB/wA5nT2tvbaf+Y2gyag8ShH8w6VwWV6bcpbVyiE9yUdR4Jmty9m3vA/AvbaD2vMQI6iN/w'
                                'BKP6R+o/B73Y/85Wfkldw+rceZrnS3/wCWe6068Z/vt4Zl/wCGzFOgzDp9rvIe0+gkLMyPfE/oBavv+crfyStI'
                                'zJB5mudTYCvo22nXit8v38US/jhHZ+Y9PtCz9p9BHlMn3RP6QHzD+en/ADkx5Q/MryleeT9H8o38kc80Vxba1q'
                                'MkUD200D1Dxwxety5LyQ1dfhY5sNHoJ4p8RLznbXtFh1uE4oQPMGzQojuAv3c3xWGZGV0Yo6EFWXYgg1BBzbPJ'
                                'B+hf5Y/85kaQmlWWk/mZYXcWpWcSwt5lskE8dzx25zw1VkcilSnIE1NF6ZpdR2UbvGdu57vs72shwCGoBsfxDe'
                                '/eOnwv4Pb0/wCcqPyKZFdvOzRMRUxtpmpch7HjakfjmJ/Juo/m/aP1u4HtLoP9U/2Mv1PmD/nJj83vyj/NHytp'
                                '9r5d1G7vvMug3on0u6NlLFE0MwCXETNMEYBgFf7PVAM2XZ2lzYZkyGx83nvaDtTR63EBjJM4nbY8jz5/jZ8beX'
                                'LvTtP8xaDfaxFNNpNlqNrPqkMCq0r28cytKsauyKWKAgAsBXuM2+QExIHOnldPKMMkTP6QRfuvd+lR/wCc2vyq'
                                '/wCrB5r/AOkSx/7Ls5/+Rc3fH5n9T3/+i3SfzZ/If8U89/NT/nLfyL5w/L3zV5X8u6P5htdX12z+p2899Baxw'
                                'KkjqJubR3crCsfICinfw65k6XsjJjyxnIigfP8AU4XaPtNg1GnnjhGQlIVuBXn1PR+e/T6N86F4p9g/lX/zl75'
                                'p8m2VtoPnLT385aPagR2uoer6eowxjYKXYMs4AG3OjeL0oBqNX2PDKeKB4T9n7HqOzvabLp4iGUccR1/iH6/xu'
                                '+rdJ/5y9/JTUV5XusajoLca8L7T53Nf5a2guBX8M1U+xtSOQB+P66ejxe02inzkY+8H9Foi9/5y4/I+1Vmg8x3'
                                'mpEdEttNu1J+XrxxD8cEextSecQPiGUvaTRDlIn3A/pAeU+af+c3/ACittcW3ljyVqOsvMrRFtWeG0t2VhQ1SM'
                                '3DOtD0PGvtmbg7AyE3OQHu3/U6/Ue1mKiMcCffQH6Xw9+V3mzy/5R/Mzy55w8wWFy2h6NfSX0mn6ciyzKypIYF'
                                'iWeWMELIU3Z60FdztnQavBPLhlCJ3Ird5Ps/UY8GpjlmDwg3Q+yr8/N+gn/Q8P5T/APUvebf+kSw/7L85v/Q/q'
                                'P50fmf1PZ/6K9L/ADZ/If8AFPD/AM9P+coPKH5jaL5W0ry3oesIuj+YbTWdVg1aK2ijuIbRZAIAYp7ivIvvVab'
                                'ZsezeyMmnlKUyN4kCr6/AOr7W7exaqEIwjLaQkbreunMvnLzt5v0fWtGs7K0lm1C9CWkct5OrBylrDwM0zSFm9'
                                'eRy5ZUZowDUEuzMdvpsEoSJOw3+39H2/B0uq1MMkABudvsHM+Z+Xxt5PmeHXqZOSZOO2FVuTCtE5IMgtOEJWnJ'
                                'hK05MKGjhDJTOEIdkwqw5NksOEKtJyaVuEJDROSDIrOuTCtE5MJUz1wpbJyShbklWn8MkGQfQ2fObxbsVdirsV'
                                'diricVU8IV2SSFhySVmSS0cISspkwlxyQVZ1yQVxyQZKZP9uTCho4WS3JKHeOTCqRyQZBrJKsP45IKX0t/zjz+'
                                'Smg/m0PNU/mO91Kxs9D+qR2Z06SGNpJbj1S/IzQzCiiMdAOuVZchhVPUeznYeLtHxDlMgI1VV1vvB7n0t/wBCa'
                                'flh/wBX3zR/0lWX/ZFlP5mXk9P/AKDNH/On84/8S1/0Jn+WH/V+80/9JVl/2Q4fzUvJf9Bmj/nZPnH/AIlr/oT'
                                'P8sD/ANL7zT/0lWX/AGQ4fzc/Jf8AQZo/52T5x/4lr/oTH8r/APq/eaf+kqy/7IcP5yfcPx8U/wCg3R/zp/OP/'
                                'Eu/6Ex/K/8A6v3mn/pKsv8Ashx/Oz7h+Piv+g3R/wA6fzj/AMS1/wBCYfld/wBX7zT/ANJVl/2Q4fzs+4fj4r/'
                                'oN0f86fzj/wAS4/8AOGH5Xn/pfeaf+kqy/wCyHD+fn3D8fFf9Buj/AJ0/nH/iWv8AoS78rv8Aq/eaf+kqx/7Ic'
                                'P8AKGTuH2/rT/oN0f8AOn84/wDEu/6Eu/K3/q/eav8ApKsf+yHD/KGTuH2/rX/Qdo/50/nH/iVv/Qln5W/9X/z'
                                'V/wBJVj/2Q4/yjk7h9v61/wBB2j/nT+cf+Jd/0JZ+Vv8A1f8AzV/0lWP/AGQ4f5Sydw+39af9B+k/nT+cf+JaP'
                                '/OFf5Wn/pf+av8ApKsf+yHD/KeXuH2/rX/QfpP50/nH/iWv+hK/yt/6v/mr/pKsf+yHH+VMvcPt/Wv+g/Sfzp/'
                                'OP/EtH/nCr8rD/wBL/wA1f9JVj/2Q4R2rlHQfb+tf9B+k/nT+cf8AiWv+hKPyr/6v/mr/AKSrH/shw/ytl7h9v'
                                '60/6ENJ/On8x/xKhP8A84YflHaxmW58z+ZraIdZJb2wRfvaxAwjtXMeQHyP60S9ktGNzOfzj/xLEr//AJxt/wC'
                                'cadL5fpL82buwK9Vn13R4z9zWoOXR7Q1R5Q+w/rcWfs/2ZD6sxHvlD9TC7/8AK3/nELTa/WPzh1mTj1+q3Vvdf'
                                'd'
                                '9X02SuXx1OtPLGPx8XGn2b2PDnnl8CD90WFX/l/wD5xAtK/V/PHnzVKdBawwLX5fWNPh/HL4z1p/hiPx73Eng7'
                                'HjyyZD7q/TEMK1B/+cZYuQ063/My9I6GafR7dT8iIJT+GZERqzz4PtcSf8mD6fGPxgP0FhOoX/5T1K6Z5W82n+'
                                'Wa61+wH3omjn/iWZEY5uso/I/8U4sp6T+GE/jOP/EMLvpdJcn9G2V3aDsLm6juD96W8OZERLqR+Pi40zA/SCPe'
                                'b/QEtywNa05IKsyTJackErDk1awsgtOSSsyYVonJBKzClo5IK1k6VbhZhbkwlacmFW4UhacklbkghacmAkLSe9'
                                'PowpWnJpWHCrWSDILCckEtdMmErGPXJKGhkgladzkgrumSCQpk5Jk+iM+cninYq7FXYq7FVpOKrcIUNZMMlhyS'
                                'hbhSsP4ZMMg10GSCFp/DJBLQySVrZMJWZIJcT7YQq3JJWk5MKFPJsmicUrMkEP05/wCcQdG/R/5X3WpstJNe1m'
                                '5mR/GKBY4FH0Oj/fmHqDcn1L2PwcGjMv50j8ht99vqrKHq3Yq7FXYq7FUPcXdraJ6t3cxWsQ6yTOqL97EYQLYy'
                                'kI7k0xK+/Mj8vdMr+kPPfl+zZeqS6laq3/AmSp+7JjFM8gfk4s+0dND6ssB/nD9bDb7/AJyF/JnTuX1jz9YSce'
                                'v1ZJ7r7vQikrlg0uU/wuHPt/QQ55R8LP3Bht9/zlt+TVpy9DU9S1Pj/wAs1hKtfl6/o5YNBlPc4c/avQx5En3'
                                'A/ppht/8A85reQIq/o7ytr94R0M62tuD9KzSn8MtHZs+pDiT9sdMPphM++h+ksMv/APnOFviXTfy4H+TNc6pX'
                                '70S1/wCNstHZffL7HEn7Z/zcXzl+z9LC77/nNf8AMKXkNO8seX7MHoZkup2H0ieIfhl0ey8fUlxJ+2OpP0wgP'
                                'mf0hhl//wA5bfnRd8vq+r6dpden1XT4Wp8vrAly6PZuHuJ+LiT9qddLlID3AfpthV//AM5DfnRqPIXH5g6jHy'
                                '6/VVhtf+TEcdMvGhwj+EOLPt3XT55T8KH3AMLv/wAx/wAwtTr+kfPXmC+VuqT6ldOvy4tJTLo4MY5RHycSfaG'
                                'pn9WSR/zj+th9xc3N1IZbq4kuJT1klcux+liTl8RXJxZSMtybQ+SCQ45JK3JhVhyQVbkmS04VaySrSfbJhIWZI'
                                'JWnJBKyuSUOyQZLG/2skErcmFWHvkkhrClb1PyyQVx8MkEhYckyaOTCVmSpWjkgkLDkgrWSCrDk2S04Qq0/qy'
                                'YSs+jCEgNHbJBkpnc5MKHH8MkErDkkuO23bJIWjJJW5IMgs6/Rkgr6Jz5xeLdirsVdirjiqw/LFDWSZBacmlT'
                                'ySWjhCVvU5MJaJySrDvkgrskEhTJyYSGumFktP6skFDskFKmx3yYCQtySVhwhLWSCgPt38u/+coPJv5feQPLf'
                                'lODyxq2oXmkWzLeS1ghheeWR5pSjc3Yjm5oSoPtmPLTmcibe67O9qMGi0sMIhImI35AWTZ6o2+/5zZmPJdN/L'
                                'tE/lludSLfeiWy/8SxGk82yftuf4cPzl+xh99/zmb+YcvIaf5d8v2SnoZY7qdh8j68Y/DLBpI95cOftnqj9MI'
                                'D5n9LDL7/nK785rrl6GtWWmV/5ZrC3any9dZssGlx9ziT9qtfLlID3RH6bYdffn7+cWoV+sfmBqacuv1Yx2v3'
                                'egkdPoywafH3OHPt7XT55ZfDb7qYXfef/AD5qZb9I+ddevweq3Go3Mg+5pDlsccR0Dh5Nfqcn1ZJH3yP62LTz'
                                'zTyGS4leaRuskjFmP0nfLgHGJJ3KHOSVo5IJCnklayQZLTkktZIIWMcmEhTyTJo4VWnJUrWSDILTkgEtH2yYS'
                                'sPX2yShr6MISsyQVo++SCrPoybJrpkgqmf1ZJLWFIaOSZKffLArR/DJBVnXCycckq0ZJWskGYWZIJaOTCrckk'
                                'LThSsyQVo5MKsySVpyQVYcklrJBkFrZIKtHf8ADJgMlpyShYO5OSCXHJK1hSFhybJbkgofROfODxTsVdirsVWn'
                                'FVuEBWjkwyWnvklCzClae+SDINDJhVp/Vkgq33yQVonJBkp98kEhxwpW5JLRyaFLLGTRxVYd8kFdkgypackEr'
                                'ckFWE5MJCzvhS0ckrskFWHJgJW+OSCVrH7skErckkNHJBKzClxyaFInJsgtwpWn8MkFW5JIcckyW5IKtOTCrO'
                                'uSZBo4VW5IKtOTCQtw0lYcmErDkldhDMLDkgq3LAq0nrkkrcISt75IBXZIJC05JktyYCVhyQVrpkkhYflhVrJ'
                                'qtOSSsOSCVuSSsOFQHdPpyQZqZyYUOyYSpk5JId0GSVb3yStHCGQUzklayYZB9FZ83vEuxV2KuxVYcVaySQ0'
                                'cmEqZOSCWjhCrMkycemTVYT7ZIK1kgkLGOSStyTJaflhCuyYVYxyYSFmSStOFK3JBQ4nJBkpnJK0cmFUycky'
                                'a7YQrWSVo5IKsJybJo5IBVM5JXZIM1pySVuEIWtkwkKZybJrCqw5IK1kgyDRyQSt7ZMJWHw+7JBQ1hSt75IK0'
                                'fHJKsOTZLckFWHJBK3CkNHJBksO+TCtHJhVM74WTjklWjJK0ckyC09ckErTkwlbklC04QyWHrkgho5MJWnJJ'
                                'WHJBK05JVuEMgtOSCVmTCWicmoWYQlxyahrphSsPyyTJbkgrRyYS+is+bniXYq7FWjiqzCFayQZLT8smqzCl'
                                'ackEhaP1dskElxyYVZkgrjkgyUj4UyQSHHClbklaOTVTPXJhkGsKqZyQUuyTILTkglbkgq0nJJUzkkuO3vkg'
                                'rWSCrScmErMkEtE5IJWfRklAayQZLMKXZNCmxyYZBZhStOEKtyaQ3kmSzvkgq05MJWZJIaOFLWSCFhyYSFuF'
                                'K05MJWHJK1hDILSeuSCVvjk1WE/dk0hbhCWj1yQVrtkkhaflkmS3JBK05MKtwpC0/hklW5IKtJyYSsyQStO'
                                'SSsOFXZIM1Mn+3JhQ7pkwlYcKhrp2yQStPX9WSCtHJBIWHJJayYZBackFfRefNrxLsVdiq0nFVuSCQ0ckEqZy'
                                'QS12ySrDkmTug98mhYcIS19GSCVjZMJW++SZNHCFa6ZIKtILEKoLMTQKNyTXtkwEgIi/0+/0q8n07VLK402/'
                                'tG4XVjdRvDNE1AeLxuFZTTxGSBtsyY5Y5GMwQRzB2KCOSDFaVIoSpAYVUkdflkgtNZIMlhySrckAqwnJBkFS'
                                'G3nnkhhhgkmmuWCW0KKWaRmPEKqgVJJ2AGFkIkkADm67tbqwurmxvbeWzvbOV4Ly0nQpJFLGSro6MAVZSCC'
                                'CKg5IG+SzgYExkKI5hQOTYrDk2Sc6J5a8x+ZZZrfy5oGpeYJ7ZPUuYNNtJrt40JoGdYUcgV2qcBnGPM03YN'
                                'NlzkjHEyI7gT9yE1fRdY0G6NhrukXui3wUObO/gktpeJ6HhKqtQ08MnGQluDaM2HJilwziYnuIpK8sDALTk'
                                'mS3CELScmEhaQ3ENxPGtOVNq+FckypZ0ySq1nZXupXdtp+nWk1/fXsqw2dlbRtLNLI5oqRxoCzMSaAAVw2I'
                                'iyyhCU5CMRZPIBP9Z8j+dfLdst55i8n63oNozBFutR0+5tYyx6KHljUVPzyMM0JmoyB9xcjLo8+EXOEojzB'
                                'H3sVOXBoa7ZMKpnJhLXTClacKtZNUw0nR9T1/UYdJ0ayfUNRuFkaC0jpyYQxtLIRUj7KISfljOYgOKRoNuL'
                                'FLLLhiLP4KDs7S5v7u1sLOFri7vZkgtYF+08kjBUUe5JAyZIAs8giMTIgDmWr+yutMvbzTr+Bra+0+eS2vL'
                                'd6co5YmKOhp3VgRkokSAI5FM4GEjE8xsgsmxCLsbC+1S8tdO0uyn1HULyRYrOwtYmmmlkY0CRxoCzMewAri'
                                'ZCIsmgG2EJTkIxFk9AgnVlYo6lHUkMpFCCOoIyyLHk0FZq8VLEAkgb0A6n6MmEqRySUytNG1S/0/VtUs7KSf'
                                'T9CSGTV7pacYEuJRDEX3H2pGCinfIyyRiREnc8vvbI4pSiZAbDn8dkq75aGtonJhkFpwgJWnJhK05MKGjhDJ'
                                'TOEIdkwqw5NktOEBVhOTStwhIaJyQZFZ1yYVonJhKmeuFLZOSULckq0/hkgyCzJBWjkgyW5NQ+jM+bHiXYq4'
                                'nFVPCFdkkhYcklZkktHCErKZMJcckFWde2SCuOSDJTJ+jJhQ0cLJb9GSUO8cmFep/kv5bm8x+ftPkXT5NUt'
                                'vLUE2vXthEvN51sF9WKEL39Wb046f5WCZqLuOw9Kc+pBqxAGZHfw7gfE0PizX80vLPmC+1D8tvNvnHSLnTt'
                                'V83LFpXmuC4QxO95YTLAJSRSnrWzREHxDeGMCNwHP7V0uWcsObNEiU/TK9vVE1fxjX2savfJ3l+HWvz7s47'
                                'Jhb+Rvrn+Gk9WQmD0tZhs0qeVXpE5X46+PXJCRqPn+pxp6LEMmrAG2O+Hc7VMR+O3eyjzBZaX510/8A5x+8'
                                'rWOiW+gy+YofqqajFPcTNbwy6tdwSIqTSFWBYmXf4q/CDx2xiTHiP45OZqMcNVHSYoxEeIVdk0DOQPM/HvY'
                                '1f6N5H8xaP+YieXPLs3l2+/L+Nb3T9Qe7nuDqFot4lpIt2k3wJKfVV19MINivE9csBkCLPNxsmDTZsebwoG'
                                'Jx7g2TxC+E8V8jve1d1Mx0jyl+Wdx5j8i+R7/yncmXzh5TsdU1DzPDqE4uLa8n09rovbwMTCVLJurhuu1AK'
                                'ZEylRN8i5uHSaOWXFgljNzxiRlxGwTG9hy+dvNPMGm+VNY8gQ+cPLvl1/LVzY+Yk0K6sVu5r1bmK4tZLiKU+'
                                'tuJF9JlbjRTUUUZdEkSom9nW58WHLpvGxw4CJ8NWZWCCQd+u3u8mdeY/wAuPLqeV/ObweXYfK+r+T9Ptb+0S'
                                'XW4r7VpVa4gglXU7GKV1gZhNyAVU4misDXIxyGxvd+W3wdhqOzsQw5KhwSgAR6xKZ3APHEE8PPuFcig/N1zom'
                                'saJ+QOnReW4NLW/tqGaC5umdLc6vdQyQL6krbO1ZOX2gdgQu2SgCDPf8Ux1cseTHpYiAFjvPLjII59efelV15V'
                                '8saNqP5x+ZNV0uTW9M8meZTouheX5LmaNJpbm7ulV7m4jb1ysUVuf2gWYj4tjWQlI8IG1i2qWlw45ajLOPEIT'
                                '4Yxs72TzPPYDv3PVMtL8heS9U88/l3P+jrmDyj568vahrF1oH1hzNazWUF8skUU7UcoJbUPGz1qDQ8h1JySEZ'
                                'b7g19zbi0GnnqMJo+HkgZGN7ggS2B51cbF/awfzLpvlbVPy/0/zp5e8vN5YuLbX5dCv7Bbya8jnQ2q3MM/Kap'
                                'VxRlYLRTsQB0y6BkJ8JN7W4epx4cmmGbHDgInwkWTe1g79ed9E6/KW0S+8pfnFaSa3beXEl0XTa6zeGcQQ01'
                                'a2b4zbRyyfFTiOKHc70FTgzmpQ2vc/c39kw4sGoHEI+mO5uh6h3An7GUebtBfVX/I/wDKi48wN5hv7+f6ynnI'
                                'K7W/1HXJoUgjtHm4ySJD6TsQ4WjfCAKEZHHKuPJVeXucrVYPE/LaUz4iTfH04ZkUI3uQKPPrsl/5geSPI9h5'
                                'X8y3emW+jeX9U8uX9vFoiWvma01e71a0klaCU3NrHO5imj+CT92qrTkCvw8snhyzMgDZB8qr4sddosEMUzERj'
                                'KJFVMTMhdGxexGx2AHNNNU8n/lvc+dPMn5Zad5Vm0vUbfQ5dQ0bzT+kLiWRb230sakY3gcmL0XCshqOQ68+wE'
                                'cmQQGQm9+VedNuTSaWWeemjCjw2JWfqEePlyr7fNhGn6R5G8seXvy9uvM/lqbzPe/mB9Yur2dLue2On2Ud41nG'
                                'LVYDxkmJidz6gYfZXh3y4ynOUhE1w/aatw8eLT4MeI5YcRyWTuRwxvh2rmdid79ybQeS/J3kwfnQ/mbRH85N+'
                                'XetadpuiRfXJbJJVuZ7uJjO1ua0KRKxC0NRQEb4fFnPg4TXEDfXuboaPBpvzHiR4/DkANyOZPOvcl93qmjv/w'
                                'A49WUEflm2guH853MCXwuLpnWZbG2ka44mTgWZCIypHGgqBy3yUYy/Mc/4fLvLGWSH8nAcAvxCLs86G/Pu27v'
                                'ij9X8m+SD5LutS8t+X5PMdlaaFb3cvnDS9UWbUbTU2SIzpqelOy+jbLKXTksewo3qNWgYZZ8dSNb8iNq8j3tm'
                                'XSYPAMsceICIPEJXIS2vjh0jdjl52Xnn5MH/AJC3+W3/AIEmm/8AUQmZGr/uZ+4/c4PZH+OYv64+96et7pPkaz'
                                '/NIax+ZOneak806VqGlad5P0pr65DXlxKphubg3NvDDH9WK8wQS1RRdq1o4ZZTCoEUQbNcv2uzE4aaObjyiXF'
                                'EgRFncnYmwAOH5oHS/KPkDT9V/LLyNrnl+41bU/zG03TLzUPNcd3NDNYS62xFqtpbpWF1hVkL+orljyA40ycsu'
                                'QxnOJoRJ2rnw87/AGMMel08J4sM4knIIkys+nj5UOW213d+SA8tflvoGq2mktexknyp5u1DTvzFuoZX4zaVa2r'
                                'X6yr8VI/3VldKCtK/D3yeTUTiTXWIMffdfpDHT6DHMRv+GZE/6oHFfltGSB88eQtA8s6R5lvbS2aZtc80Wlp+X'
                                'k8krgJpMtmNRZz8XGQmK8tFJatN++WYM8pyiD0ieL33X6Cx1eix4YTIH1TAh/Vri+6UWf8AnP8AKnyJ5esPOnl'
                                '9/wBDadqPlHS3n0rzW3ma0l1HUdRtFRprabSPrBMazfvBGqoJFIXkWqQKMGryTMZbkSO44TQB68VdOvRzdV2bg'
                                'xRyQ9IMRtLjHFKQ5gwva962sPPfM/lzyjBY/lf5W0Ty2YPNHnnSdHv77zRPezusct7NJAyR23IRgMQCxJ/1Qu9'
                                'cnFkyXOcj6Ykiq7vNw9RgwiOLHCPrnGJMrPU1y5Mw/MD8t/Iei6H54s7OPR9G1Pyayr5e1VPM9nf6hrDQXC29x'
                                'Fd6ak7GF2UtKqxxqU48GrlWm1WWUoE2RLmOEgR22o1v3OTrNBgxwyAcIMOR4wZS3o3G9j12ArkU78j6Z5L8mfm'
                                'd5W8lQ+V5bnzJF5ee+vvObX0wdry/0OS9ZI7b+4MCpN6Y+HnUcufbI55ZMuGWQy9PFVV0Eq587cjSY8On1MMQh'
                                '6uG+KzzMOLlyreu/wA3zF5D/wCU58l/9t3Tv+omPNvqP7qXuP3Og0f9/D+sPve4+c9N8jecNR/PGHTPLMugeZP'
                                'I9zfa3b679emnOoJFqiW13Hcwv+6TkbgPH6aqRTieXXMHTzy4hiJlcZUKrltYrr03t2+qx4c8s4jHhlAmV2Txe'
                                'qjY5ddqS2+8g+T4LLU/Pqaa/wDgufyFbatpFiJ5iqa9dyDS/q3q8/UYRXkc0xUt9laHbJx1OQkY79fHR/qj1X8'
                                'RQYy0eIA5q9HhggWfrPor4Ss+5g/5E/8Ak5Py2/7b9n/ycGZXaP8Ai2T+qXF7J/xvF/WCd6RYeSdL/L/WPO3mL'
                                'ym3mnVY/OZ0e1tXvrizt/Qe0edvV9AhmoVNOJU1O5IHExnLLLMMcJcI4L5A9a6t2OGGGCWWcOI8dcyBVX0ei+V'
                                'tK8s+RPzT/NDQ7XQF1bS/8DalqelLeXVwssFrdaAb97RmheMPzScRMxHIcaqQd8xs08mfT45GVHjANAcxKr+y3'
                                'O0+PHp9TliI2PDJFk7Aw4q299fcxH8v/IPly/8AJl1591PQtH1d9T8wz6VpXl3V/MUWgWlta20Mc80iTz3EUs0'
                                'n79UQcjxClnDVAy/VamccoxRJFRskR4iSduVbcv1NGj0mOWE5pRBuVAGXAABudyQSd9vmbVr3QtD8taL/AM5K6'
                                'L5Z1WLWtAs7bQDpOoQzxXStDLqtrKqGeAtG7R8+DFTTkp6dMMMk8s9PKYqRMrHL+E9CmWKGKGpjA3ECNG7/AIh'
                                '1G23JD3vkDyfBY6n5+j01x5Kn8g22raRYCeZlj1+7kXSvq3q8/Ub0ryOaYqW+wtD8OSjqspIxX6/EIP8AUHqv4'
                                'xoIlo8QBzV6PDBA/pn018JWfcnPlbyb+Wtr5n/KDyB5g8nz69fefrDStW1rzMNRuLaSI6qTLDb28MR9L0kj4rI'
                                'WBdiW4shAyOfUZzjy5YToQJAFA/TzJPO+7p727T6bTjJhxThZmASbI+roByqufX3JJ+X/AOXXl6XyXdedNY0nS'
                                'fMM135in0XTdG1rzFB5etYre0hjlnmE0k8LyysZlVVBotCzBqgZbqtZMZRjiTGo2SImZsnYVRobNek0cDiOSQ'
                                'EiZUAZCAoDc3Ys7/BoeSPy30PV/wA7riSH/HPl3yJZaffeVntNSULJ9dvrSJY5Lq0LxyBVuPTkK9aNxKNQrL8z'
                                'qMkcI+iUyRKx3A9D7rH6V/LYMc8x+uMACKPeR1HvosZ80aX5T0jVfy68yaT5JF/o3nrQvrreRXvbx1S9+t3Ni'
                                'Y4Z42FwVLwq6AuWqaGuZGnyZZxyQlOjCVcVDlQO45dd2nNjxwljnGFicb4bPOyNjz6bKH5z2HknQb3Q/LXl3y'
                                '3BoPmjSrZm8+/U726vbaK+mKstjG1zLLVrZRxkZTQyFl/ZyXZk82QSnOVxJ9NgA1/O2A+rp5e9PaMcOMxhCNS'
                                'A9VEkX3b93XzeI5tg6xacmAlaT3p9GFK05NKw4VayQZBYTkglrpkwlYx65JQ0MkErTuckFd0yQSFMnJMmskFC'
                                '05MJWnphSH0bnzY8Q7FVpOKrcIUNZMMlhyQULcKVhyYZBroMkELT+GSCWhkktNkwlTwpcT7ZIKtySVpOTChPt'
                                'N8zX+k6D5j8v2kUAt/NAtU1K8ZWNwIrSUzLFGwYKEd+LOCpJ4ruN8JjZty8WqljxTxxqp1Z60Dde4nn7gvs/N'
                                'mp2Ply98sRpBJYXWpWurwTOr+ta3dqjxiSBgwUc1ej8latFpSmHh3tlj1c4YTiFUZCXmCL5e/qzHV/ze1bV7L'
                                'zRbN5a8v2N550hWLzRrVrbTrd3TrPHcerVrho42LxgsERVapJWtCrHGBW/Jzc3bE8scg4IA5B6iAbO4N86HLo'
                                'AD90afz1qx0byppiW1rb3vkq5M/l3zHEJVvoUM73Ihr6npFFmcuCY+QO3KlRkxAWfNx/z8/DxxoA4z6Zb8Q3Jr'
                                'nVWb5X5o/XvzM1PWtO1nT7fQ9H8v8A+JporjzTeaXDMkuoyROZV9X1ZpURfU+MrEqKWANOgwxx18G3P2nPLCU'
                                'RGMeM3IxBuVb72SBvvQoWo2/5la5beY/LXmiO0sG1DyrpNvo+nQmOUwvBbWrWiNKolDFyjEkhgK9qbZLwxRHe'
                                'xj2lkjlhlAFwiIjnVAcO+/OmP2/mvUrXyy/laBIEsn1mDXBdBW+sLc28MkCBW5cONJSSONagb9ss4BdtMdVO'
                                'OHwhVcQlfWwCP0s21P8AOTV9UtfNML+V/Llre+dbZrfzRrFvazrdXTmWOb1uRuCsbc4wSEVUJJLKTxKxGECtz'
                                's5+Xtic4zHBAHIKkQDZ3Bvnsdum3eOTFz57v20fyjpUumWE03kq6M+iau6zfWRCZ3uTayUlEbRGVy32OQ6BgN'
                                'ss8Pcnvcb89LgxxMR+7Ng73V3R3qrPdfmjLX8ydWh1bzhqF7pmm6vp/nu6kvPMvly7Sb6lLK073KMnpTRzRmJ'
                                '3bgyy1AJBJqcPhCh5M4dpTE8kjESGQ3KJvh530IIo8t2/+VoeYF806Z5qjtdPil0TTZNI0XR0ikWxtLOW3mtv'
                                'SjQSCSgE7vVpCS5qxO+TGEcNd7L+U8vjRy0PSOED+ECiKG99SefPmxj/ABLf/wCEz5O9GD9GHVv0yZ+Lev8AW'
                                'BAbfjy5ceHHenGte/bLBAcXF5U435mXg+Dtw8XF53VfL4NaT5ov9F0bzVodrDbvaebbW3tNSklVjIiW1zHdoY'
                                'SrAAl4gDyB2r33yRgJEHuTi1UsWOcABUwAfgRLb5I0eetcTSPKmlRmGKXyTqEt/wCWtaVXF5bGV0lMKvy4GNZU'
                                '9RQUqGJ3oaYjELJ7+baNbkEIR/mG4nqOte69+XNF+avP7eaYbsP5R8u6Pf6ncLdavrGnWsqXNzMvIlqzTTJCHL'
                                'cmECpyPXbbDjw8HUls1Wu8cG4QBJskA2T8Sa8+Gno35h/m5byeZfM8vlHStFZ9X0yDSh53iguF1FrSSyhhuY15'
                                'yiFWNGjMno8+O3LvlWDTekcROxuunN2Gv7VHizOKMdwI8dHirhAI515Xw3XVgGh/mbqWi6Xo+lXWg6N5jj8s3'
                                'Ml35WutVhnkl06WVxK4i9GeFXQyDnwlV15b065kS04kSQSL511cHB2jLHCMTGMuE3HiB9PuojbrRsWkLeeNdl0'
                                'zzjpt28V+3nq+tdR17UZ1Y3LXFrLNMGRlZVHNp2LVU9qUy3wY3Ej+Hk1/nMhhkid+Mgk9bFn9O6na+b7u38nah'
                                '5Km06yv9MvL9dTs7qcSi4srsIsTyQNHKi/vI1CsHVhTcAEVwnEDMTvfl71jqiMJwkAgm+tg+W/Ubb2yW4/NrWJ'
                                'bDUIo9A0O01vVtJ/Qer+bILeVL65sTGkTI6+sbYM6IFZ1hDEd675GOlFjc0DddL+/7XIPaczEjhiJGPCZUeIjl'
                                '38PLrVsG8seYL3yp5i0PzNp0cM19oN7Bf2cVyrNC0kDh1EgRkYqSN6MD75fkxicTE8js4mmzSwZI5I84kEX5JT'
                                'eXMl5dXN3IFEl1K80gWvEM7FiBWppv45YBQpjKRkSe96ZpP5ua5pVpoQOjaPqOueVLY2flXzZeQzPf6fBV2jSP'
                                'jMsD+k0jGIyxOU7bUpTLSRkTuQDzHQ/p97sMXaeSAj6YmURUZEHiiPnW3SwaY1oXnzzB5c0fzjounyxta+ebWO'
                                '01uWYM8vGOQvzjYMKMwZ0JYH4XYdTUXT08ZyjI/w8mjDrMmKE4R5TFH8fMfEqfmLzzrvmjRfKOhao0JsvJdnJY'
                                '6S0SsrskjhuUxLEMwVUjBAHwIopUVyWPBHHKUhzkbKc+syZoQhLlAUP2/YPcAnfmL80b/zRaXJ1fyx5euPMV/a'
                                'x2mpeczaStqVwkXEB25zNbrKQgBlWEOR+0DkcelGM7SNd17frrytuz9oSzA8UI8RFGVeo/bV+dWxjXPN2ra7L5'
                                'amnENnN5U0q10nSp7QOj+lZu7xSOWdv3lXNStB0oBl+PDGHEB1JJ+LRm1M8pgTtwgAV5fpZB5q/My582wag1/5'
                                'T8uWuu6yUbXPNVtZyLfXTo4kaQiSZ4InkYVd4YkZtwTQkZHDpRiIqUqHIXsP0/Mlv1GvOcG4R4jzkBuftoX1IA'
                                'tO9K/O7XdLOj3reWfL2peYtD039D2fmu9trh742Iha3SJ+FykRKRPwEnp8+IALdawloIyscUhEm6FVfPuvn0um'
                                '/H2tOHCeGJkBw8RBuqqudctrq/N5NpOpz6Lq2l6xapHJdaVdw3ltHKCYzJA6yKHClTQld6EZnTgJxMT1FOux5'
                                'DjkJDmCD8novmL83dW1+w8yWsXlvQPL935ynWbzbrOlW88V1fKs31gRP6s8kcaGUBmESKXIHIneuNi0McZieKR'
                                'EeQPIdO773PzdpTyxkOGMTP6iAbO99+2/cBfVGeZ/NMOn/AJVeVvyzsPMUHmGuqTeYtZls0lWC09WFY7axDzRx'
                                'NI0ZaaSSg4BnopJBOODCZZ5ZTGtuEX17z9wDPPqBHTQwCXFvxGrobbR3AvqT0svOPKfma/8AJvmbRPNWlxQT6'
                                'hoF5He2UN0rNC0kRqokVHRiPGjD55mZsIzQMJciKcPT55YMkckecTe6vN5u1KXyrceUGgthptzrf6eecK/ri5'
                                '9BrfgG58eHFiaca1/a7ZKOCIyeJ1rh+F2yOokcXh7VxcXndV8mQr+auvDzvL55m0/Tbi8u9LTRtR0eSOb6jc2'
                                'I01NLeKRRMJfjgQFisgPLcU6ZX+Sh4XhAmgbB2sG+Lu7/ACcga+fjeKQLIojeiOHh775eaH0P8yLnRtL1Xy9d'
                                'eWdE8w+V9S1A6rB5b1OO6aCzvOPAS2skNzDOh4AIQZTyUANU75LJoxOQmJESAqxVkedgj7EYtaYRMDGMok3Rug'
                                'fKiD9qWf471MWnnmwh07TLS18/C1XU7e1tvQjt0tLpLqJbSOJlRByQKeStUf5XxZaNLG4GzcLrfnYrdh+blUwA'
                                'AJ1dCqo3szHzR5rg078qPK35Y2HmODzCf0rP5j1mWzSVYLT1YUjtbAPNHE0jRlppJKAoGeikkE5RgwGWplnMa'
                                '24RfXvl9wHXZys2cR00MAlxb8RrkO6O9X1J6bvUfyy/MjyvosHkXzJ5s1ryxqdz5CtHitIbrTtTbzJDHDJK8F'
                                'haMlbCVCWHCaU8ogzfZIU5h63R5JmcMcZATPQx4OlyP8Q8wObsNDrMcBCeSUTwDqJcfWoj+E+RPJ4R5f8AzIv'
                                'tE0bUvLl/oGj+bPLmo336UXRdYjuGjt77hw+sQSWs9vKjMoCsOdGAAIzbZdEJyExIxkBViuXcbBH2Orw6wwiY'
                                'GIlEm6N7HvFEH7UtXz5qiW/nq0g07TLS28/wwQapb21t6EdtHbXcV5GtpHEyogDwqp5BqrX9o8st/KRuBJNwu'
                                't7uwRv82A1UqmKFTq9uVEHb5J7oP5ua5oGqeQtXi0bRtRn/AC50+fT9AhvYbh4yJ557j1pRHPGxlje4YoyFeNF'
                                'NKiuVZezoZI5I8UhxmzVdwFcuW27fh188coSoHgFC77yb5899mM+avNdl5lETQeS9D8sXCyvNc3mlNqLS3Bk6'
                                '+sb6+uwd96qAa9TmTp9OcXOcpe/h293DENOfOMvKEY+69/8ATEsNzLDjLDk2S04Qq0/qyYSswhIDR2yQZKZ3O'
                                'TChx/DJBKw5JLjtt2ySFoySVuSDILOv0ZIK0ckGS05NVpwsn0dnzW8O44qsOKGskyC05NKnkktHCErepyYS0T'
                                'klWHfJBXZIJCmTkwkNdMLJaf1ZIKHZIKVNjvkwkLcklYcIS1kgoDRyQZLDklaOTVTJ36ZJk10GEK1/mckFaP4'
                                'ZMJWHJJaOSCQp5JWskGS05JLWSCFjHJhIU8kyaOFVpyVK1kgyC05IBLR9smErD19skoa+jCErMkFaOSCrDk2T'
                                'XTJBVM/qySWsKQ0ckyU++WBWjkgqzrhZNHJK0Mkq3JBmFuSCWifbJhVmSUNHCyWZIIaOTCVmSStOSCrDkktZIM'
                                'gtbJBVo7/hkwGS05JQsHcnJBLjklawpCw5NktyQUNHJBK3JJCw/qwpfR+fNbw604qtwgK0cmGS098koWYUrT3y'
                                'QZBoZMKtP45IKt98kFaJyQZKffJBIaP4YUtZJQ0cmqllgZNHFKw75IIdkgypackErckFWE5MJCzvhS0ckrskF'
                                'WHJhK3JBK1j92SCVuSSGjkglZhS45NCkTk2QW4UrT+GSCrckEhxyTJbkgq05MKs65JkGjhVbkgq05MJCzCAla'
                                'cmErDkld2whmFhyQVblgVaTkkhbhCVvfJAK4/LJBIWHJMmsmErDkgrXTJJCw/qwq1k1WE5JktOSCrcklYckoDu'
                                'n04QzUzkwodkwlTJySQ7oMkq3vklaOEMgsOSVbkwyC05JWskGSw98IV9IZ81PDrDirWSSGjkwlTJyQS0cIVZk'
                                'mTj0yarCfbJBWskEhYxySVuSZLT8sIV2TCrGP3ZMJCzJJWnClbkgocckGSmckrRyYVTJyTJrthCtZJXHJKpk5'
                                'Nk0ckAqmckrskGaw5JLWSCFrZIJCmcmyawqsOSCuyQZBackAlb2yYSsPh92SChrClZ3yQVxyarDkmS3JBVhyQS'
                                'twpDRyQZLDvkwrRyYVTO+Fk45JVuSVo5IMgtPXJBK05MJW5JQtOEMlnfJBDR6ZMJWnJJWHJBK05JVuEMgtOSCV'
                                'mTCWicmoWYQlxyahrphSsPyyTJbkwFaOSCVuSStO2FKzJBX0gc+aXh1mEK1kgyWn5ZNVmFK05IJC0fq7ZIJLR'
                                'yYVbkgrjkgyUj4UyQSHHClbklDRyaqZ65MMg1hVYckFLWSZBackErckFWk5JKmcklxyQVoZIKtJyYSs8ckEt'
                                'E5IJWfRklAayQZLDhS7JoU2OTDILMKVpwhVuTSHHJMlvfJBVpyYSs75JQ0cLJbkghacmEhbhStOTCVhyStYQy'
                                'CwnJBLXjk1WE/dk0hbhCWj1yQVrtkkhaf1ZJktyQStOTCrcKQtOSVbkgq05MJCzJBK05JKw4VdkgzUyf7cmFD'
                                'umTCVhwqGunbJBK09f1ZIK0ckEhYcklrJhkFpyQVacIZLDkgrWSCvo8nPmh4dbkgkNH5ZMJUzkglrthVTOSZN'
                                '9B75NCw4QlrJBKxsmErffJMlpwhXdMmErGP35IKFmTS0cISsyQWnZIMlhySrckAqwnJBkFoyQVbklbOSVYcmy'
                                'W4QFWE+2TS0ckEhackyW4QhaTkwkKZybKmjhVYckFdkgyC04QlrtkwFUzkwlrphStwq1k1WHJpW4QErDk0rcK'
                                'hrJBmsOTCtZIKsOSZNYVW98kFaJyYZBacICVpyYStOTCho4QyUz1yQQ7JBVhybJackFWH8MkErcISGiaZIMlP'
                                'r/HJhXE5MJUz1wpbJyShb75JVp/DJBkFmSCtHJhktyShacLJZkgrRyYV9Hd8+Zg8O7JpCw5JKzJJaOEJWUyYS'
                                '45IKs69skFccmGSmT9GSCho4WS36Mkod45MKpHJgMgGu2FVh/HJBS1kkho5IMlmSCrScklTOSS7JBWu+SCrT8'
                                'skErTkkrTkwlZklawhksOSS7JBCxj7b5MMgp5JLRwqtyahrJBktwhLRyYSpnc5NQ47fRhDJbkgELTkgkLMkla'
                                'cmErDklawsgtOSCVnvkwrRyaQsxS0ckFa6ZOlC3CzW5MJWnJhVuFIWnJJW5IIWnJgJW++FK05NKw4VayQZrCc'
                                'kFa6ZMJWk5JIWjJBVp3OSCu6ZIJCmcklrJBIWnJhK04Qlacklbkgq0nJhIfR+fMweGDWTDJYckFC3ClYcmGQa'
                                '6DJBC0/hkglod8klpsmEqeFLRyQVrJBktJyYQFPJsmjiEhZkgh2TDJacKVmTCrDkglaMKWjk1dkgqw98mGS3C'
                                'FWnJpWnCkBacmyW4Qho5MJCmckyC3pklWnCFayQZBaflkktZMKsOSCrfc5JktOFWsmq0n2yQSFmSCVpyQSsOS'
                                'UOwhkpnJhLWTCrCeu2SZBrthVb1OSCuPhkgkLDv7ZIMmjkwlZkqVo5JKw5IK1klWHJslpwhVpyYSswhIDR2yQ'
                                'ZKfU+GTChxyQSsOSS47bdskhaMklbkgyCzCFaOTDJacmq04WSw4QrjkwqkTk2T6Sz5meGC05NKnkktHCErepy'
                                'YS0ckqw75IK7JBkpk5MKGumFktP6skFDumSCqbHfJhIW5JKw4QlrJBQGjkgyWHJBWjk1Uyd+mSZNdsIVrqckF'
                                'aP4ZMJWHJJaOSCQp5JWskGS05JLWSCFjHJhIU8kyaOFVpyVK1kgyDRyQCVpPt0yYSsP4d8koa+jCErMkFaOSCr'
                                'Dk2TXTJBVh/HJBK3CkLTkmSzvlgVonJBKzrhS0ckrXuckq3JBmFuSCWifbJhVmSUNHCyWZIIaOTCVmSStOSCrD'
                                'kktZIMgtbJBVuTDJackoWDuTkglxyStYUhYcmyW5IKGjkglZkkhaf1YUrcmFWtkwlTwhL6SOfNAeHWnvklCzC'
                                'laf9rJBkGh40yYQVp/HJBLXvklWk5IMlPvkgkNH8MIS1k1DRySqWWBk0cUrMkEOyQZUtOSCVuSCrCcmEhZhS0'
                                'ckru2SCrDkwlbkglackErckkNHpkglZhS45NCkTk2QW5JK04Qq3JBIcffJMluSCrTkwqzvkmQaOFVuSCrTkwk'
                                'LMICVpyYSsySuwhmFhOTCrcmFWk5JIW4Qlb+rvkgrj8skEhYckyaOTCVhyQVrpkkhYf1YVayarCckyWnJBVuS'
                                'SsOSUB2EM1PJhQ45MJUyckkO6ZJVuFWjkgyCw5JVuTDILTklayQZLD3whDWTCVM/jk2SzCFf/2Q== '
                    }],
                'attachments': []
            }
        }

        email = template_renderer.compose_email_report_object(report, report_items)

        assert email['email_data']['html'] is not None
